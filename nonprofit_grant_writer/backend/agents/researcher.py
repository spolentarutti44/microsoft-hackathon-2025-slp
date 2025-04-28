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
    Uses Bing search for finding relevant information.
    """
    
    def __init__(self):
        """Initialize the researcher agent with search capabilities."""
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
        logger.info(f"BING_SEARCH_API_KEY loaded: {'Yes' if self.bing_search_api_key else 'No'}")
        
        if not all([self.azure_endpoint, self.azure_api_key, self.deployment_name]):
            raise ValueError("Azure OpenAI credentials not properly configured in .env file")
        
        if not self.bing_search_api_key:
            logger.warning("Bing Search API key not found. Search functionality will be limited.")
        
        # Initialize Azure service
        self.azure_service = AzureChatCompletion(
            deployment_name=self.deployment_name,
            endpoint=self.azure_endpoint,
            api_key=self.azure_api_key
        )
        
        # Initialize DuckDuckGo search plugin (no API key required)
        from .duckduckgo_connector import DuckDuckGoConnector
        self.search_plugin = WebSearchEnginePlugin(DuckDuckGoConnector())
        
        # Create the researcher agent, including search plugin if available
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
            plugins=[self.search_plugin] if self.search_plugin else []
        )
    
    async def research_grant(self, grant_url):
        """
        Research a specific grant opportunity.
        
        Args:
            grant_url (str): URL of the grant to research
            
        Returns:
            dict: Information about the grant
        """
        if not self.search_plugin:
            logger.warning("Search plugin not available. Research capabilities limited.")
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
        if not self.search_plugin:
            logger.warning("Search plugin not available. Research capabilities limited.")
            return {"error": "Search capabilities not available"}
        
        context = f"I need to research the nonprofit organization '{nonprofit_name}' with website {nonprofit_website}. Please provide information about this organization including:\n\n1. Mission and vision\n2. Programs and services\n3. Target population served\n4. Impact and achievements\n5. Leadership team\n6. Funding sources\n7. Any recent news or developments\n\nPlease format your response as a structured JSON object."
        
        result = await self.agent.complete_chat_async(context)
        return result.content 