import logging
import urllib
from httpx import AsyncClient
from semantic_kernel.connectors.search_engine.connector import ConnectorBase
from semantic_kernel.exceptions import ServiceInvalidRequestError

logger = logging.getLogger(__name__)

class DuckDuckGoConnector(ConnectorBase):
    """A search engine connector that uses the DuckDuckGo Instant Answer API for web search."""

    async def search(self, query: str, num_results: int = 1, offset: int = 0) -> list[str]:
        """
        Perform a DuckDuckGo Instant Answer API call and return top snippets.
        """
        if not query:
            raise ServiceInvalidRequestError("query cannot be empty.")
        # DuckDuckGo Instant Answer API endpoint
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
            "skip_disambig": 1
        }
        try:
            async with AsyncClient(timeout=5) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                snippets: list[str] = []
                # Use AbstractText if available
                if data.get("AbstractText"):
                    snippets.append(data["AbstractText"])
                # Collect related topics' text
                related = data.get("RelatedTopics", [])
                for item in related:
                    if isinstance(item, dict) and "Text" in item:
                        snippets.append(item["Text"])
                    elif isinstance(item, dict) and "Topics" in item:
                        for sub in item["Topics"]:
                            if "Text" in sub:
                                snippets.append(sub["Text"])
                    if len(snippets) >= num_results:
                        break
                return snippets[:num_results]
        except Exception as ex:
            logger.error(f"DuckDuckGo search failed: {ex}")
            raise ServiceInvalidRequestError("DuckDuckGo search failed.") from ex 