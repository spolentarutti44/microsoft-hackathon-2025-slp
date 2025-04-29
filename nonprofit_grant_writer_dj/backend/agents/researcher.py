import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.core_plugins.web_search_engine_plugin import WebSearchEnginePlugin

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger(__name__)

class ResearcherAgent:
    """
    Agent responsible for researching grant opportunities and nonprofit information.
    Search plugins are injected by the orchestrator.
    """
    def __init__(self, search_plugins=None):
        """Initialize the researcher agent with injected search plugins and Azure service."""
        # Azure Chat completion service setup
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not all([azure_endpoint, azure_api_key, deployment_name]):
            raise ValueError("Azure OpenAI credentials not properly configured in .env file")
        self.azure_service = AzureChatCompletion(
            deployment_name=deployment_name,
            endpoint=azure_endpoint,
            api_key=azure_api_key
        )

        # Use injected search plugins or none
        self.search_plugins = search_plugins or []

        # Create the researcher agent with injected plugins
        self.agent = ChatCompletionAgent(
            service=self.azure_service,
            name="ResearcherAgent",
            instructions="""
            You are the Researcher Agent. Your role is to gather information about:
            1. Grant opportunities and their requirements
            2. Nonprofit organizations and their missions
            3. Relevant statistics and data to support grant applications
            4. Similar successful grant applications

            You have access to web search tools to find this information. Always cite your sources
            when providing information. Focus on finding accurate, relevant, and up-to-date information
            that will strengthen the grant application.
            """,
            plugins=self.search_plugins
        )
    
    async def research_grant(self, grant_url):
        """
        Research a specific grant opportunity.
        
        Args:
            grant_url (str): URL of the grant to research
            
        Returns:
            dict: Information about the grant
        """
        if not self.search_plugins:
            logger.warning("Search plugins not available. Research capabilities limited.")
            return {"error": "Search capabilities not available"}
        
        # Example of how to use the agent to perform a search
        context = f"I need to research the grant opportunity at {grant_url}. Please provide details about this grant including the following information:\n\n1. Grant provider/organization\n2. Application deadline\n3. Funding amount\n4. Eligibility criteria\n5. Focus areas or priorities\n6. Required application components\n7. Evaluation criteria\n\nPlease format your response as a structured JSON object."
        
        result = await self.agent.complete_chat_async(context)
        return result.content
    
    async def research_nonprofit(self, nonprofit_website, nonprofit_name):
        """
        Research a specific nonprofit organization.
        
        Args:
            nonprofit_website (str): URL of the nonprofit's website
            nonprofit_name (str): Name of the nonprofit organization
            
        Returns:
            dict: Information about the nonprofit
        """
        if not self.search_plugins:
            logger.warning("Search plugins not available. Research capabilities limited.")
            return {"error": "Search capabilities not available"}
        
        context = f"I need to research the nonprofit organization '{nonprofit_name}' with website {nonprofit_website}. Please provide information about this organization including:\n\n1. Mission and vision\n2. Programs and services\n3. Target population served\n4. Impact and achievements\n5. Leadership team\n6. Funding sources\n7. Any recent news or developments\n\nPlease format your response as a structured JSON object."
        
        result = await self.agent.complete_chat_async(context)
        return result.content 