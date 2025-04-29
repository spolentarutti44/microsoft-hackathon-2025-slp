import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion

logger = logging.getLogger(__name__)

class FileSurferAgent:
    """
    Agent responsible for processing and analyzing files.
    """
    
    def __init__(self):
        """Initialize the file surfer agent."""
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
        
        # Create the file surfer agent
        self.agent = ChatCompletionAgent(
            name="FileSurferAgent",
            description="Processes and analyzes files for grant applications.",
            instructions="""
            You are the File Surfer Agent. Your role is to process and analyze files for grant applications:
            
            1. Extract relevant information from documents
            2. Analyze PDFs, Word documents, and other file formats
            3. Identify key points in grant guidelines
            4. Organize file content into structured formats
            
            Focus on extracting accurate information efficiently, formatting it for use by other agents.
            """,
            service=self.azure_service
        )
    
    async def process_file(self, file_content, file_type):
        """
        Process a file and extract relevant information.
        
        Args:
            file_content (str): Content of the file
            file_type (str): Type of the file (PDF, DOCX, etc.)
            
        Returns:
            dict: Extracted information from the file
        """
        # This is a placeholder implementation
        # In a real implementation, you would use libraries to process different file types
        # and then use the agent to analyze the extracted text
        
        context = f"""
        I have a {file_type} file with the following content:
        
        {file_content[:1000]}
        (Content truncated for brevity)
        
        Please extract the key information from this file that would be relevant for a grant application.
        Focus on identifying:
        
        1. Any specific requirements or guidelines
        2. Eligibility criteria
        3. Funding priorities
        4. Application deadlines
        5. Budget constraints or requirements
        
        Format your response as a structured summary.
        """
        
        result = await self.agent.complete_chat_async(context)
        return {"file_type": file_type, "extracted_info": result.content} 