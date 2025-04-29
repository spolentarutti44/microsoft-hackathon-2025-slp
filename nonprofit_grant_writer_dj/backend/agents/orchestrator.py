import os
import logging
import asyncio
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel import Kernel
from semantic_kernel.planners.function_calling_stepwise_planner import FunctionCallingStepwisePlanner

from .researcher import ResearcherAgent
from .writer import WriterAgent
from .nonprofit_grounding import NonProfitGroundingAgent
from .quality_checker import QualityCheckingAgent
from .scraper import ScraperAgent
from .web_surfer import WebSurferAgent
from .file_surfer import FileSurferAgent
from .duckduckgo_connector import DuckDuckGoConnector
from .bing_search_connector import BingSearchConnector
from semantic_kernel.core_plugins.web_search_engine_plugin import WebSearchEnginePlugin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Orchestrator agent that coordinates all other agents to generate grant content.
    """
    
    def __init__(self):
        """Initialize the orchestrator agent."""
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
        
        # Setup Kernel for orchestration
        self.kernel = Kernel()
        self.kernel.add_service(self.azure_service, self.deployment_name)

        # Initialize search connectors as tools
        duck_plugin = WebSearchEnginePlugin(DuckDuckGoConnector())
        bing_key = os.getenv("BING_SEARCH_API_KEY")
        if bing_key:
            bing_plugin = WebSearchEnginePlugin(BingSearchConnector(bing_key))
            self.search_plugins = [duck_plugin, bing_plugin]
        else:
            self.search_plugins = [duck_plugin]

        # Initialize all other agents, passing search tools
        self.researcher_agent = ResearcherAgent(search_plugins=self.search_plugins)
        self.writer_agent = WriterAgent()
        self.nonprofit_grounding_agent = NonProfitGroundingAgent()
        self.quality_checking_agent = QualityCheckingAgent()
        self.scraper_agent = ScraperAgent()
        self.web_surfer_agent = WebSurferAgent(search_plugins=self.search_plugins)
        self.file_surfer_agent = FileSurferAgent()

        # Register each agent as a plugin so the planner can invoke their functions
        self.kernel.add_plugin(self.researcher_agent.agent, "ResearcherAgent")
        self.kernel.add_plugin(self.writer_agent.agent, "WriterAgent")
        self.kernel.add_plugin(self.nonprofit_grounding_agent.agent, "NonProfitGroundingAgent")
        self.kernel.add_plugin(self.quality_checking_agent.agent, "QualityCheckingAgent")
        self.kernel.add_plugin(self.scraper_agent.agent, "ScraperAgent")
        self.kernel.add_plugin(self.web_surfer_agent.agent, "WebSurferAgent")
        self.kernel.add_plugin(self.file_surfer_agent.agent, "FileSurferAgent")
        
        # Create orchestrator agent
        self.orchestrator = ChatCompletionAgent(
            service=self.azure_service,
            name="OrchestratorAgent",
            instructions="""
            You are the Orchestrator Agent. Your role is to coordinate all other agents to generate 
            comprehensive grant content for nonprofit organizations. You will:
            1. Break down the grant writing task into subtasks
            2. Assign each subtask to the appropriate agent
            3. Collect and integrate the results from all agents
            4. Ensure the final grant is well-structured and meets all requirements
            5. Ensure the final grant aligns with the nonprofit's mission and values
            Always maintain a professional tone appropriate for grant applications.
            """
        )
    
    def generate_grant_content(self, nonprofit_website, grant_url, nonprofit_name, nonprofit_mission):
        """
        Generate complete grant content based on the provided information.
        
        Args:
            nonprofit_website (str): URL of the nonprofit's website
            grant_url (str): URL of the grant being applied for
            nonprofit_name (str): Name of the nonprofit organization
            nonprofit_mission (str): Mission statement of the nonprofit
            
        Returns:
            dict: Dictionary containing all sections of the grant
        """
        # Log the start of the process
        logger.info(f"Starting grant generation for {nonprofit_name}")
        
        # Create a list of all agents for the orchestration
        agents = [
            self.orchestrator,
            self.researcher_agent.agent,
            self.writer_agent.agent,
            self.nonprofit_grounding_agent.agent,
            self.quality_checking_agent.agent,
            self.scraper_agent.agent,
            self.web_surfer_agent.agent,
            self.file_surfer_agent.agent
        ]
        
        # Define the task for orchestration
        task = f"""
        Generate a comprehensive grant application for {nonprofit_name} (website: {nonprofit_website})
        applying for the grant at {grant_url}. The nonprofit's mission is: "{nonprofit_mission}".
        
        The grant should include the following sections:
        - Executive Summary
        - Problem Statement
        - Project Description
        - Goals and Objectives
        - Implementation Plan
        - Evaluation and Impact
        - Budget
        - Sustainability Plan
        - Conclusion
        
        Format your response as a JSON object with these fields as keys.
        Output only the JSON object, with no additional text, commentary, or markdown fences.
        """
        # Orchestrate using function-calling stepwise planner
        planner = FunctionCallingStepwisePlanner(service_id=self.deployment_name)
        # Use asyncio to run the planner invoke function
        result_model = asyncio.run(planner.invoke(self.kernel, task))
        # Extract the final answer from the planner result
        response_text = result_model.final_answer
        
        # Log the planner output for debugging
        logger.info(f"Planner final_answer: {response_text!r}")
        if not response_text or not response_text.strip():
            logger.error("Planner returned empty final_answer. Check planner configuration and tool responses.")
        
        # Extract the first complete JSON object using brace matching
        text_to_parse = response_text
        start = text_to_parse.find('{')
        if start != -1:
            depth = 0
            end_idx = -1
            # Iterate from the first '{' to find matching closing '}'
            for i in range(start, len(text_to_parse)):
                char = text_to_parse[i]
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            # If we found a matching end, slice out the JSON block
            if end_idx != -1:
                text_to_parse = text_to_parse[start:end_idx+1]
            else:
                # Fallback to everything after first '{'
                text_to_parse = text_to_parse[start:]
        
        # Parse the result into a structured format
        try:
            # Sanitize JSON string before parsing
            import json, re
            # Unwrap quotes if the JSON is wrapped in single quotes
            if text_to_parse.startswith("'") and text_to_parse.endswith("'"):
                text_to_parse = text_to_parse[1:-1]
            # Remove literal newlines, tabs, and carriage returns
            text_to_parse = text_to_parse.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            # Remove non-breaking space characters
            text_to_parse = text_to_parse.replace('\xa0', ' ')
            # Remove other control characters (except legit whitespace)
            text_to_parse = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text_to_parse)
            # Load planner output JSON, allowing control characters
            try:
                grant_content = json.loads(text_to_parse, strict=False)
            except TypeError:
                # For Python versions where json.loads doesn't accept strict, fallback to JSONDecoder
                grant_content = json.JSONDecoder(strict=False).decode(text_to_parse)
            # Include nonprofit info for the UI overview section
            grant_content['organization_info'] = {
                'name': nonprofit_name,
                'mission': nonprofit_mission,
                'website': nonprofit_website
            }
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            grant_content = {
                "title": f"Grant Application for {nonprofit_name}",
                "organization_info": {
                    "name": nonprofit_name,
                    "mission": nonprofit_mission,
                    "website": nonprofit_website
                },
                "error": f"Error generating content: {str(e)}"
            }
        
        logger.info(f"Completed grant generation for {nonprofit_name}")
        return grant_content 