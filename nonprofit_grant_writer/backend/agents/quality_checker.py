import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion

logger = logging.getLogger(__name__)

class QualityCheckingAgent:
    """
    Agent responsible for evaluating and improving the quality of grant content.
    """
    
    def __init__(self):
        """Initialize the quality checking agent."""
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not all([self.azure_endpoint, self.azure_api_key, self.deployment_name]):
            raise ValueError("Azure OpenAI credentials not properly configured in .env file")
        
        # Initialize Azure service
        self.azure_service = AzureChatCompletion(
            deployment_name=self.deployment_name,
            endpoint=self.azure_endpoint,
            api_key=self.azure_api_key
        )
        
        # Create the quality checking agent
        self.agent = ChatCompletionAgent(
            name="QualityCheckingAgent",
            description="Evaluates and improves grant content quality.",
            instructions="""
            You are the Quality Checking Agent. Your role is to evaluate and improve grant application content.
            You will analyze the content for:
            
            1. Clarity and conciseness
            2. Persuasiveness and compelling narratives
            3. Logical flow and organization
            4. Proper grammar, spelling, and punctuation
            5. Appropriate tone and language for grant reviewers
            6. Evidence-based statements backed by data
            7. Alignment between goals, activities, and evaluation metrics
            8. Realistic timelines and budgets
            
            Provide specific, actionable feedback to improve the quality of the content, and suggest
            edits to strengthen weak areas. Focus on making the grant application as competitive as possible.
            """,
            service=self.azure_service
        )
    
    async def evaluate_content(self, content):
        """
        Evaluate the quality of grant content and provide a quality score.
        
        Args:
            content (dict): The grant content to evaluate
            
        Returns:
            dict: Evaluation results with score and feedback
        """
        context = f"""
        Evaluate the quality of the following grant application content:
        
        {content}
        
        Please analyze the content based on the following criteria:
        1. Clarity and conciseness
        2. Persuasiveness
        3. Logical organization
        4. Grammar and mechanics
        5. Appropriate tone
        6. Use of evidence and data
        7. Alignment between goals and methods
        8. Realism of timeline and budget
        
        For each criterion, provide a score from 1-10 and specific feedback for improvement.
        Format your response as a JSON object with the following structure:
        {{
            "overall_score": 0-100,
            "criteria_scores": {{
                "clarity": 1-10,
                "persuasiveness": 1-10,
                "organization": 1-10,
                "grammar": 1-10,
                "tone": 1-10,
                "evidence": 1-10,
                "alignment": 1-10,
                "realism": 1-10
            }},
            "strengths": [
                "strength 1",
                "strength 2"
            ],
            "weaknesses": [
                "weakness 1",
                "weakness 2"
            ],
            "improvement_suggestions": [
                {{
                    "section": "section_name",
                    "issue": "description of the issue",
                    "suggestion": "specific suggestion for improvement"
                }}
            ],
            "summary": "brief summary of evaluation"
        }}
        """
        
        result = await self.agent.complete_chat_async(context)
        
        # Attempt to parse the response into a JSON structure
        try:
            import json
            
            # Try to extract just the JSON part if there's surrounding text
            content = result.content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                evaluation = json.loads(json_str)
                return evaluation
            else:
                # If no JSON found, return a default structure
                return {
                    "overall_score": 0,
                    "criteria_scores": {},
                    "strengths": [],
                    "weaknesses": ["Could not parse evaluation results"],
                    "improvement_suggestions": [],
                    "summary": "Evaluation parsing failed. Raw response: " + content[:100] + "..."
                }
        except Exception as e:
            logger.error(f"Error parsing quality evaluation: {e}")
            return {
                "overall_score": 0,
                "criteria_scores": {},
                "strengths": [],
                "weaknesses": [f"Error: {str(e)}"],
                "improvement_suggestions": [],
                "summary": "Evaluation failed due to an error"
            }
    
    async def improve_content(self, content, evaluation):
        """
        Improve grant content based on quality evaluation.
        
        Args:
            content (dict): The original grant content
            evaluation (dict): Quality evaluation results
            
        Returns:
            dict: Improved grant content
        """
        context = f"""
        Improve the following grant application content based on the quality evaluation:
        
        Original Content:
        {content}
        
        Quality Evaluation:
        {evaluation}
        
        Please revise the content to address the identified weaknesses and improvement suggestions.
        Focus particularly on areas that scored below 7 in the criteria scores.
        Return the complete improved content as a JSON object with the same structure as the original content.
        """
        
        result = await self.agent.complete_chat_async(context)
        
        # Attempt to parse the response into a JSON structure
        try:
            import json
            
            # Try to extract just the JSON part if there's surrounding text
            response_content = result.content
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                improved_content = json.loads(json_str)
                return improved_content
            else:
                # If no JSON found, return the original content with an error
                logger.error("Could not parse improved content")
                return {**content, "error": "Improvement failed - could not parse response"}
        except Exception as e:
            logger.error(f"Error parsing improved content: {e}")
            return {**content, "error": f"Improvement failed: {str(e)}"} 