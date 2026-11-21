"""Offline tests for the CrewAI team and hierarchical task configuration."""
from unittest.mock import MagicMock

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
    import crew.agents as agent_module
    captured = {}

    class FakeLLM:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(agent_module, "LLM", FakeLLM)
    create_llm("test-key")
    assert captured["model"] == MODEL_NAME
    assert captured["api_key"] == "test-key"


def test_three_specialist_agents_have_expected_tools():
    # CrewAI validates LLM objects with Pydantic; a MagicMock is not a valid LLM.
    # Constructing an LLM does not make a network request.
    llm = LLM(model=MODEL_NAME, api_key="test-key", temperature=0.2)
    researcher, analyst, writer = create_agents(llm)
    assert "Research" in researcher.role
    assert len(researcher.tools) == 1
    assert "Analyst" in analyst.role
    assert len(analyst.tools) == 1
    assert "Writer" in writer.role
    assert not writer.tools


def test_tasks_are_unassigned_for_manager_delegation():
    tasks = create_tasks("Tech Sector Q3 Analysis", "data/sample_financial_metrics.csv")
    assert len(tasks) == 3
    assert all(task.agent is None for task in tasks)
    assert "Tech Sector Q3 Analysis" in tasks[0].description
    assert "data/sample_financial_metrics.csv" in tasks[1].description
    assert "executive summary" in tasks[2].description.lower()


def test_task_factory_rejects_blank_query():
    with pytest.raises(ValueError, match="query"):
        create_tasks("   ", "data/sample_financial_metrics.csv")


def test_crew_uses_hierarchical_process(monkeypatch):
    import crew.crew as crew_module
    # Use valid CrewAI model/Agent/Task objects. No crew kickoff occurs here,
    # so this remains an offline configuration test.
    fake_llm = LLM(model=MODEL_NAME, api_key="test-key", temperature=0.2)
    monkeypatch.setattr(crew_module, "create_llm", lambda api_key=None: fake_llm)

    result = build_market_research_crew("topic", "metrics.csv")
    assert result.process == Process.hierarchical
    assert result.manager_llm is fake_llm
    assert len(result.agents) == 3
    assert len(result.tasks) == 3
    assert all(task.agent is None for task in result.tasks)
