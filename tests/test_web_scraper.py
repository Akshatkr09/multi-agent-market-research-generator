from tools.web_scraper import MAX_CONTENT_CHARS_PER_SOURCE, _execute_search, _format_search_results

class FakeTavilyClient:
    def __init__(self, response):
        self.response = response
        self.calls = []
    def search(self, **kwargs):
        self.calls.append(kwargs)
        return self.response

def test_search_uses_raw_content_and_expected_settings():
    client = FakeTavilyClient({"results": [{
        "title": "Market outlook", "url": "https://example.com/market",
        "content": "Short summary", "raw_content": "Full extracted page text"
    }]})
    result = _execute_search("  technology market outlook  ", client)
    assert "Market outlook" in result
    assert "https://example.com/market" in result
    assert "Full extracted page text" in result
    assert client.calls == [{
        "query": "technology market outlook", "search_depth": "basic",
        "max_results": 5, "include_raw_content": True, "include_answer": False
    }]

def test_formatter_falls_back_to_snippet_when_raw_content_missing():
    result = _format_search_results({"results": [{
        "title": "Example", "url": "https://example.com", "content": "Snippet fallback"
    }]})
    assert "Snippet fallback" in result

def test_formatter_handles_empty_results():
    assert _format_search_results({"results": []}) == "No web sources were returned for this query."

def test_formatter_limits_extracted_text_per_source():
    long_text = "x" * (MAX_CONTENT_CHARS_PER_SOURCE + 500)
    result = _format_search_results({"results": [{"title": "Long", "raw_content": long_text}]})
    assert long_text not in result
    assert "x" * MAX_CONTENT_CHARS_PER_SOURCE in result

def test_empty_query_is_rejected_before_api_call():
    client = FakeTavilyClient({"results": []})
    try:
        _execute_search("   ", client)
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
    assert client.calls == []
