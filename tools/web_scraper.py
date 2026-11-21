"""Tavily-backed web search and page-content extraction tool."""
from typing import Any
from crewai.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY
MAX_CONTENT_CHARS_PER_SOURCE = 10_000
DEFAULT_MAX_RESULTS = 5
def _format_search_results(response: dict[str, Any]) -> str:
    results = response.get("results") or []
    if not results: return "No web sources were returned for this query."
    sections = []
    for index, item in enumerate(results, start=1):
        title = str(item.get("title") or "Untitled source").strip()
        url = str(item.get("url") or "").strip()
        snippet = str(item.get("content") or "").strip()
        raw_content = str(item.get("raw_content") or "").strip()
        extracted = (raw_content or snippet)[:MAX_CONTENT_CHARS_PER_SOURCE]
        sections.append(f"Source {index}: {title}\\nURL: {url or 'Not provided'}\\nSearch summary: {snippet or 'Not provided'}\\nExtracted page text:\\n{extracted or 'No page text was available.'}")
    header = f"Tavily research results ({len(results)} sources)"
    if response.get("answer"): header += f"\\nTavily answer: {response['answer']}"
    return header + "\\n\\n" + "\\n\\n".join(sections)
def _execute_search(query: str, client: Any) -> str:
    cleaned = query.strip() if isinstance(query, str) else ""
    if not cleaned: raise ValueError("The research query must not be empty.")
    response = client.search(query=cleaned, search_depth="basic", max_results=DEFAULT_MAX_RESULTS, include_raw_content=True, include_answer=False)
    return _format_search_results(response)
@tool("Web Research and Extraction")
def web_research_tool(query: str) -> str:
    """Search the web for a research topic and return source URLs plus extracted page text."""
    if not TAVILY_API_KEY: return "Tavily API key is missing. Add TAVILY_API_KEY to your local .env file, then retry."
    try: return _execute_search(query, TavilyClient(api_key=TAVILY_API_KEY))
    except ValueError as exc: return f"Invalid research query: {exc}"
    except Exception as exc: return f"Tavily research request failed: {type(exc).__name__}: {exc}"
