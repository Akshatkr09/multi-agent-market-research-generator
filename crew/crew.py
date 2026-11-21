"""Factory for the manager-led hierarchical market research crew."""
from crewai import Crew, Process

from crew.agents import create_agents, create_llm
from crew.tasks import create_tasks


def build_market_research_crew(
    query: str,
    csv_path: str,
    api_key: str | None = None,
    verbose: bool = True,
) -> Crew:
    """Build a hierarchical crew whose manager assigns the unbound tasks."""
    llm = create_llm(api_key=api_key)
    agents = create_agents(llm)
    tasks = create_tasks(query=query, csv_path=csv_path)
    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=verbose,
    )
