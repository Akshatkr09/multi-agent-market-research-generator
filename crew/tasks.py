"""Manager-assignable task definitions for the hierarchical crew."""
from crewai import Task


def create_tasks(query: str, csv_path: str) -> list[Task]:
    """Create tasks without fixed agents so the manager can delegate dynamically."""
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("The research query must not be empty.")
    if not csv_path or not str(csv_path).strip():
        raise ValueError("A financial CSV path must be provided.")

    research_task = Task(
        description=(
            f"Research the market topic: {clean_query}. Use the web research tool. "
            "Gather current industry developments, market context, competitor "
            "activity, and relevant risks. Prefer credible sources, include source "
            "URLs, and clearly flag information that could not be verified."
        ),
        expected_output=(
            "A source-attributed research brief with key findings, industry trends, "
            "competitor insights, risks, and source URLs."
        ),
    )
    analysis_task = Task(
        description=(
            f"Analyse the financial dataset at this CSV path: {csv_path}. "
            "Use the Financial Data Parser tool to calculate descriptive statistics. "
            "Explain the mean, minimum, maximum, standard deviation, and any notable "
            "patterns. Do not fabricate missing values or claim causation."
        ),
        expected_output=(
            "A concise financial analysis containing the Pandas summary table, "
            "interpretation of the available metrics, and data limitations."
        ),
    )
    writing_task = Task(
        description=(
            f"Prepare a complete market research report for: {clean_query}. "
            "Use the research findings and financial analysis produced by the other "
            "specialists. Include an executive summary, market overview, key trends, "
            "competitor landscape where evidence exists, financial analysis, risks, "
            "conclusion, and source list. Keep facts and interpretation distinct. "
            "If a section lacks evidence, state that rather than inventing details."
        ),
        expected_output=(
            "A polished Markdown report with clear headings, evidence-based analysis, "
            "a financial statistics table, risks, conclusion, and source URLs."
        ),
    )
    return [research_task, analysis_task, writing_task]
