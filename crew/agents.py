"""Specialist agent definitions for the market research crew."""
from crewai import Agent, LLM
from config import GOOGLE_API_KEY
from tools.financial_parser import calculate_financial_metrics
from tools.web_scraper import web_research_tool

MODEL_NAME = "gemini/gemini-2.5-flash"


def create_llm(api_key: str | None = None) -> LLM:
    key = (api_key or GOOGLE_API_KEY).strip()
    if not key:
        raise ValueError("GOOGLE_API_KEY is missing. Add your Gemini API key to the local .env file.")
    return LLM(model=MODEL_NAME, api_key=key, temperature=0.2)


def create_agents(llm: LLM) -> list[Agent]:
    researcher = Agent(
        role="Lead Market Research Specialist",
        goal="Find reliable, recent market information, competitor activity, industry trends, and cite source URLs for the requested topic.",
        backstory="You are a careful market researcher. Distinguish verified facts from estimates, prioritize credible sources, and report source URLs and dates wherever available.",
        tools=[web_research_tool], llm=llm, allow_delegation=False, verbose=True,
    )
    analyst = Agent(
        role="Financial Data Analyst",
        goal="Inspect the supplied financial CSV, calculate descriptive statistics, and explain meaningful patterns without inventing data.",
        backstory="You are a detail-oriented analyst experienced with financial metrics and Pandas. Label limitations and distinguish observed values from interpretation.",
        tools=[calculate_financial_metrics], llm=llm, allow_delegation=False, verbose=True,
    )
    writer = Agent(
        role="Technical Market Research Report Writer",
        goal="Turn the research and analysis into a clear, balanced, structured market research report.",
        backstory="You write professional research reports for business readers. Preserve evidence, avoid unsupported claims, and organize findings into useful sections.",
        llm=llm, allow_delegation=False, verbose=True,
    )
    return [researcher, analyst, writer]
