import os
import logging
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.core_plugins.web_search_engine_plugin import WebSearchEnginePlugin
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

logger = logging.getLogger(__name__)

class WebSurferAgent:
    """
    Agent responsible for browsing the web to find relevant information.
    """
    
    def __init__(self):
        """Initialize the web surfer agent."""
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
        
        # Initialize DuckDuckGo search plugin (no API key required)
        from .duckduckgo_connector import DuckDuckGoConnector
        self.search_plugin = WebSearchEnginePlugin(DuckDuckGoConnector())

        # Initialize Bing search plugin (requires API key)
        from .bing_search_connector import BingSearchConnector
        self.bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
        if self.bing_search_api_key:
            self.bing_search_plugin = WebSearchEnginePlugin(BingSearchConnector(self.bing_search_api_key))
        else:
            self.bing_search_plugin = None
            logger.warning("Bing Search API key not found. Bing search functionality will be limited.")

        # Combine search plugins (temporarily use only DuckDuckGo)
        search_plugins = [self.search_plugin]
        # To re-enable Bing search plugin, uncomment the following lines:
        # if self.bing_search_plugin:
        #     search_plugins.append(self.bing_search_plugin)

        # Create the web surfer agent, including both search plugins if available
        self.agent = ChatCompletionAgent(
            service=self.azure_service,
            name="WebSurferAgent",
            instructions="""
            You are the Web Surfer Agent. Your role is to find relevant information on the web by:
            1. Searching for specific topics related to grant applications
            2. Finding statistics and data to support grant proposals
            3. Researching best practices for grant writing
            4. Finding examples of successful grant applications

            You have access to web search tools to find this information. Always cite your sources
            when providing information. Focus on finding accurate, relevant, and up-to-date information.
            """,
            plugins=[self.search_plugin]  # use only DuckDuckGo plugin
        )
    
    async def search_web(self, query):
        """
        Search the web for information.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Search results
        """
        if not self.search_plugin:
            logger.warning("Search plugin not available. Web surfing capabilities limited.")
            return {"error": "Search capabilities not available"}
        
        context = f"I need to search for information about: {query}. Please provide a comprehensive summary of the most relevant information, and include 3-5 key facts or statistics that would be useful for a grant application. Please cite your sources."
        
        result = await self.agent.complete_chat_async(context)
        return {"query": query, "results": result.content} 