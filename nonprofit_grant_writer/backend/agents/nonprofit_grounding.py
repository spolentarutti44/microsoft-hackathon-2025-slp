import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion

logger = logging.getLogger(__name__)

class NonProfitGroundingAgent:
    """
    Agent responsible for ensuring that all generated content aligns with
    the nonprofit's mission, values, and goals.
    """
    
    def __init__(self):
        """Initialize the nonprofit grounding agent."""
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
        
        # Create the nonprofit grounding agent
        self.agent = ChatCompletionAgent(
            name="NonProfitGroundingAgent",
            description="Ensures content aligns with nonprofit's mission and values.",
            instructions="""
            You are the Nonprofit Grounding Agent. Your role is to ensure that all content in the 
            grant application accurately represents and aligns with the nonprofit organization's:
            
            1. Mission and vision
            2. Core values
            3. Target population
            4. Existing programs and services
            5. Organizational capacity and expertise
            6. Strategic goals
            
            You must review all content to ensure it authentically represents the organization.
            Flag any inconsistencies, misalignments, or areas where the content does not accurately
            reflect the nonprofit's work or capabilities. Suggest specific revisions to bring the
            content into alignment with the organization's identity and work.
            """,
            service=self.azure_service
        )
    
    async def verify_alignment(self, content, nonprofit_info):
        """
        Verify that the grant content aligns with the nonprofit's mission and values.
        
        Args:
            content (dict): The grant content to verify
            nonprofit_info (dict): Information about the nonprofit
            
        Returns:
            dict: Verification results with any issues flagged
        """
        context = f"""
        Review the following grant application content and verify that it accurately aligns with 
        the nonprofit organization's mission, values, and capabilities:
        
        Nonprofit Information:
        {nonprofit_info}
        
        Grant Content:
        {content}
        
        Please analyze the content for:
        1. Consistency with the organization's stated mission
        2. Accurate representation of the organization's capabilities
        3. Alignment with the target population served
        4. Realistic goals given the organization's capacity
        5. Appropriate tone and language for the organization
        
        If you identify any issues, please flag them and suggest specific revisions.
        Format your response as a JSON object with the following structure:
        {
            "aligned": true/false,
            "issues": [
                {
                    "section": "section_name",
                    "issue": "description of the issue",
                    "suggestion": "suggested revision"
                }
            ],
            "overall_assessment": "summary of your assessment"
        }
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
                assessment = json.loads(json_str)
                return assessment
            else:
                # If no JSON found, return a default structure
                return {
                    "aligned": False,
                    "issues": [
                        {
                            "section": "general",
                            "issue": "Could not parse assessment results",
                            "suggestion": "Please review the content manually"
                        }
                    ],
                    "overall_assessment": "Assessment parsing failed. Raw response: " + content[:100] + "..."
                }
        except Exception as e:
            logger.error(f"Error parsing alignment assessment: {e}")
            return {
                "aligned": False,
                "issues": [
                    {
                        "section": "general",
                        "issue": f"Error: {str(e)}",
                        "suggestion": "Please review the content manually"
                    }
                ],
                "overall_assessment": "Assessment failed due to an error"
            }
    
    async def revise_content(self, content, alignment_issues, nonprofit_info):
        """
        Revise grant content to better align with the nonprofit's mission and values.
        
        Args:
            content (dict): The original grant content
            alignment_issues (dict): Issues identified in the alignment verification
            nonprofit_info (dict): Information about the nonprofit
            
        Returns:
            dict: Revised grant content
        """
        context = f"""
        Revise the following grant application content to better align with the nonprofit organization's 
        mission, values, and capabilities. Address the identified alignment issues:
        
        Nonprofit Information:
        {nonprofit_info}
        
        Original Grant Content:
        {content}
        
        Alignment Issues:
        {alignment_issues}
        
        Please revise the content to address these issues while maintaining the overall structure.
        Return the complete revised content as a JSON object with the same structure as the original content.
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
                revised_content = json.loads(json_str)
                return revised_content
            else:
                # If no JSON found, return the original content with an error
                logger.error("Could not parse revised content")
                return {**content, "error": "Revision failed - could not parse response"}
        except Exception as e:
            logger.error(f"Error parsing revised content: {e}")
            return {**content, "error": f"Revision failed: {str(e)}"} 