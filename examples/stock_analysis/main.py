"""Stock research crew: three agents read a company's SEC filings through SecFeed and write an investment memo.

    export SECFEED_API_KEY=sf_...        # free key: https://secfeedapi.com/signup/
    export OPENAI_API_KEY=...            # or any LLM CrewAI supports, see MODEL below
    python examples/stock_analysis/main.py NVDA

Writes memo-<TICKER>.md next to where you run it.
"""
import os
import sys

from crewai import LLM, Agent, Crew, Process, Task

from secfeed_crewai import (FinancialStatementsTool, InsiderTradesTool, RecentEightKTool, SearchTenKTool,
                            SearchTenQTool)

ticker = (sys.argv[1] if len(sys.argv) > 1 else "NVDA").upper()
llm = LLM(model=os.environ.get("MODEL", "gpt-4o-mini"))

filings_researcher = Agent(
    role="SEC filings researcher",
    goal=f"Find what {ticker}'s latest 10-K, 10-Q and 8-K reports say about its business, results and risks",
    backstory="You read primary sources, not headlines. Every claim you report comes with the filing it came from.",
    tools=[SearchTenKTool(), SearchTenQTool(), RecentEightKTool()],
    llm=llm,
)
financial_analyst = Agent(
    role="Financial analyst",
    goal=f"Judge {ticker}'s financial health and what insiders are doing with their own shares",
    backstory="You work from reported numbers. You compare periods, compute margins and growth, and flag anything unusual.",
    tools=[FinancialStatementsTool(), InsiderTradesTool()],
    llm=llm,
)
memo_writer = Agent(
    role="Investment memo writer",
    goal="Turn the research into a short, balanced memo a busy investor can read in three minutes",
    backstory="You write plainly, keep bull and bear points side by side, and never invent a number.",
    llm=llm,
)

research = Task(
    description=(f"Use the filings tools on {ticker}. Cover: what the company sells and to whom, how the latest quarter "
                 "went according to management, the three most important risk factors, and any notable 8-K events in "
                 "the last few months. Quote short phrases where useful and keep the filing links."),
    expected_output="Bullet notes grouped by topic, each with its source filing link.",
    agent=filings_researcher,
)
numbers = Task(
    description=(f"Pull {ticker}'s annual and latest quarterly financial statements. Report revenue and net income "
                 "growth, gross and operating margins, cash and debt. Then check recent insider trades: separate open "
                 "market buys from sales, and note which sales were under 10b5-1 plans."),
    expected_output="A short table of key figures with growth rates, plus a paragraph on insider activity.",
    agent=financial_analyst,
)
memo = Task(
    description=(f"Write an investment memo on {ticker} from the research and the numbers: a one paragraph summary, "
                 "bull case, bear case, key figures table, insider activity, and a list of the filings used."),
    expected_output="A Markdown memo of about 500 words.",
    agent=memo_writer,
    context=[research, numbers],
    output_file=f"memo-{ticker}.md",
)

crew = Crew(agents=[filings_researcher, financial_analyst, memo_writer], tasks=[research, numbers, memo],
            process=Process.sequential, verbose=True)

if __name__ == "__main__":
    print(crew.kickoff())
