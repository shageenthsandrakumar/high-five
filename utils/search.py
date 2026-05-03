import os
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        from tavily import TavilyClient
        _client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))
    return _client


def search(query: str, max_results: int = 5) -> str:
    try:
        results = _get_client().search(query=query, max_results=max_results)
        return "\n\n".join(
            f"- {r['title']}: {r['content']}"
            for r in results.get("results", [])
        )
    except Exception as e:
        return f"[Web search unavailable: {e}]"
