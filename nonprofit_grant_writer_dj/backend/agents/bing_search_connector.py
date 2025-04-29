import logging
from httpx import AsyncClient
from semantic_kernel.connectors.search_engine.connector import ConnectorBase
from semantic_kernel.exceptions import ServiceInvalidRequestError

logger = logging.getLogger(__name__)

class BingSearchConnector(ConnectorBase):
    """A search engine connector that uses the Bing Web Search API for web search."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ServiceInvalidRequestError("Bing Search API key is required.")
        self.api_key = api_key
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"

    async def search(self, query: str, num_results: int = 3, offset: int = 0) -> list[str]:
        """
        Perform a Bing Web Search API call and return top snippets.
        """
        if not query:
            raise ServiceInvalidRequestError("query cannot be empty.")
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": num_results,
            "offset": offset,
            "responseFilter": "Webpages"
        }
        try:
            async with AsyncClient(timeout=5) as client:
                response = await client.get(self.endpoint, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                snippets: list[str] = []
                web_pages = data.get("webPages", {}).get("value", [])
                for item in web_pages[:num_results]:
                    snippet = item.get("snippet") or item.get("name") or ""
                    snippets.append(snippet)
                return snippets
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            raise ServiceInvalidRequestError("Bing search failed.") from e 