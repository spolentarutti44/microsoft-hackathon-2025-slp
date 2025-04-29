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
    
    def __init__(self, search_plugins=None):
        """Initialize the web surfer agent."""
        # Setup Azure service
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

        # Create the web surfer agent with injected plugins
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
            plugins=self.search_plugins
        )
    
    async def search_web(self, query):
        """
        Search the web for information.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Search results
        """
        if not self.search_plugins:
            logger.warning("Search plugin not available. Web surfing capabilities limited.")
            return {"error": "Search capabilities not available"}
        
        context = f"I need to search for information about: {query}. Please provide a comprehensive summary of the most relevant information, and include 3-5 key facts or statistics that would be useful for a grant application. Please cite your sources."
        
        result = await self.agent.complete_chat_async(context)
        return {"query": query, "results": result.content} 