"""Offline tests for the CrewAI team and hierarchical task configuration."""
import pytest
from crewai import LLM, Process
from crew.agents import MODEL_NAME, create_agents, create_llm
from crew.crew import build_market_research_crew
from crew.tasks import create_tasks


def test_create_llm_requires_api_key(monkeypatch):
    monkeypatch.setattr("crew.agents.GOOGLE_API_KEY", "")
    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        create_llm()


def test_create_llm_uses_gemini(monkeypatch):
    import crew.agents as module
    captured = {}
    class FakeLLM:
        def __init__(self, **kwargs):
            captured.update(kwargs)
    monkeypatch.setattr(module, "LLM", FakeLLM)
    create_llm("test-key")
    assert captured["model"] == MODEL_NAME and captured["api_key"] == "test-key"


def test_three_specialist_agents_have_expected_tools():
    llm = LLM(model=MODEL_NAME, api_key="test-key", temperature=0.2)
    researcher, analyst, writer = create_agents(llm)
    assert "Research" in researcher.role and len(researcher.tools) == 1
    assert "Analyst" in analyst.role and len(analyst.tools) == 1
    assert "Writer" in writer.role and not writer.tools


def test_tasks_are_unassigned_for_manager_delegation():
    tasks = create_tasks("Tech Sector Q3 Analysis", "data/sample_financial_metrics.csv")
    assert len(tasks) == 3 and all(task.agent is None for task in tasks)
    assert "Tech Sector Q3 Analysis" in tasks[0].description
    assert "data/sample_financial_metrics.csv" in tasks[1].description
    assert "executive summary" in tasks[2].description.lower()


def test_task_factory_rejects_blank_query():
    with pytest.raises(ValueError, match="query"):
        create_tasks("   ", "data/sample_financial_metrics.csv")


def test_crew_uses_hierarchical_process(monkeypatch):
    import crew.crew as module
    fake_llm = LLM(model=MODEL_NAME, api_key="test-key", temperature=0.2)
    monkeypatch.setattr(module, "create_llm", lambda api_key=None: fake_llm)
    result = build_market_research_crew("topic", "metrics.csv")
    assert result.process == Process.hierarchical and result.manager_llm is fake_llm
    assert len(result.agents) == 3 and len(result.tasks) == 3
    assert all(task.agent is None for task in result.tasks)
