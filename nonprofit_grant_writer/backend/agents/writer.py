import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion

logger = logging.getLogger(__name__)

class WriterAgent:
    """
    Agent responsible for writing high-quality grant content based on research.
    """
    
    def __init__(self):
        """Initialize the writer agent."""
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
        
        # Create the writer agent
        self.agent = ChatCompletionAgent(
            name="WriterAgent",
            description="Writes high-quality grant content based on research.",
            instructions="""
            You are the Writer Agent. Your role is to craft compelling and persuasive grant application content.
            You will:
            
            1. Create clear and concise executive summaries
            2. Develop compelling problem statements
            3. Write detailed project descriptions
            4. Articulate specific goals and objectives
            5. Design comprehensive implementation plans
            6. Create evaluation frameworks
            7. Craft sustainability plans and conclusions
            
            Your writing should be professional, clear, and tailored to grant reviewers. Use active voice,
            specific details, and evidence-based statements. Avoid jargon unless it's industry-standard.
            Always make sure your writing aligns with the nonprofit's mission and the grant's requirements.
            """,
            service=self.azure_service
        )
    
    async def write_executive_summary(self, nonprofit_info, grant_info):
        """
        Write an executive summary for the grant application.
        
        Args:
            nonprofit_info (dict): Information about the nonprofit
            grant_info (dict): Information about the grant
            
        Returns:
            str: Executive summary
        """
        context = f"""
        Write a compelling executive summary for a grant application with the following information:
        
        Nonprofit Information:
        {nonprofit_info}
        
        Grant Information:
        {grant_info}
        
        The executive summary should be 1-2 paragraphs that clearly and concisely explain:
        1. Who the nonprofit is
        2. What problem they are addressing
        3. How they plan to address it
        4. Why their approach is effective
        5. How much funding they are requesting
        6. What impact the funding will have
        
        Keep the tone professional and persuasive.
        """
        
        result = await self.agent.complete_chat_async(context)
        return result.content
    
    async def write_problem_statement(self, research_data):
        """
        Write a problem statement for the grant application.
        
        Args:
            research_data (dict): Research data about the issue
            
        Returns:
            str: Problem statement
        """
        context = f"""
        Write a compelling problem statement for a grant application based on the following research:
        
        {research_data}
        
        The problem statement should:
        1. Clearly define the issue being addressed
        2. Include relevant statistics and data to illustrate the scope of the problem
        3. Explain why this problem matters and to whom
        4. Discuss current gaps in addressing this problem
        5. Set the stage for why your nonprofit's solution is needed
        
        Keep the statement to 2-3 paragraphs, and ensure it's backed by evidence.
        """
        
        result = await self.agent.complete_chat_async(context)
        return result.content
    
    async def write_full_grant(self, nonprofit_info, grant_info, research_data):
        """
        Write a complete grant application.
        
        Args:
            nonprofit_info (dict): Information about the nonprofit
            grant_info (dict): Information about the grant
            research_data (dict): Research data for the application
            
        Returns:
            dict: Complete grant application as a structured object
        """
        context = f"""
        Write a comprehensive grant application for the following nonprofit and grant opportunity:
        
        Nonprofit Information:
        {nonprofit_info}
        
        Grant Information:
        {grant_info}
        
        Research Data:
        {research_data}
        
        Create a complete grant application with the following sections:
        1. Executive Summary
        2. Problem Statement
        3. Project Description
        4. Goals and Objectives (list at least 3-5 specific, measurable goals)
        5. Implementation Plan (including timeline and key activities)
        6. Evaluation and Impact (how will success be measured)
        7. Budget (provide a reasonable, itemized budget)
        8. Sustainability Plan (how the project will continue after grant funding)
        9. Conclusion
        
        Format your response as a JSON object with these sections as keys. For the budget, 
        create an array of budget items, each with "item", "description", and "amount" fields.
        For goals and objectives, create an array of specific goal statements.
        
        Keep the writing professional, clear, and persuasive. Use concrete examples and data to
        strengthen your case.
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
                grant_content = json.loads(json_str)
                return grant_content
            else:
                # If no JSON found, return the raw content
                return {"error": "Could not parse JSON", "raw_content": content}
        except Exception as e:
            logger.error(f"Error parsing grant content: {e}")
            return {"error": str(e), "raw_content": result.content} 