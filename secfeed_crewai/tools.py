"""CrewAI tools for SEC EDGAR data via the SecFeed API. Set SECFEED_API_KEY in the environment."""
from typing import Literal, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from . import core


class FilingQuestion(BaseModel):
    ticker: str = Field(..., description="Stock ticker, e.g. NVDA")
    question: str = Field(..., description="What you want to find out from the filing")
    section: Optional[str] = Field(
        None, description="Optional: business, risk, mdna or market_risk. Picked from the question when left empty.")


class SearchTenKTool(BaseTool):
    name: str = "Search latest 10-K"
    description: str = ("Reads the company's latest annual report (10-K) and returns the passages most relevant to the "
                        "question, with a link to the filing. Good for business model, risk factors and full-year results.")
    args_schema: Type[BaseModel] = FilingQuestion

    def _run(self, ticker: str, question: str, section: Optional[str] = None) -> str:
        return core.search_filing(ticker, question, "10-K", section or None)


class SearchTenQTool(BaseTool):
    name: str = "Search latest 10-Q"
    description: str = ("Reads the company's latest quarterly report (10-Q) and returns the passages most relevant to the "
                        "question, with a link to the filing. Good for the most recent quarter's results and outlook.")
    args_schema: Type[BaseModel] = FilingQuestion

    def _run(self, ticker: str, question: str, section: Optional[str] = None) -> str:
        return core.search_filing(ticker, question, "10-Q", section or None)


class FinancialsInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker, e.g. NVDA")
    form: Literal["10-K", "10-Q"] = Field("10-K", description="10-K for annual figures, 10-Q for the latest quarter")


class FinancialStatementsTool(BaseTool):
    name: str = "Financial statements"
    description: str = ("Income statement, balance sheet and cash flow figures from the latest 10-K or 10-Q, taken from "
                        "the filing's XBRL data, with the last few periods side by side.")
    args_schema: Type[BaseModel] = FinancialsInput

    def _run(self, ticker: str, form: str = "10-K") -> str:
        return core.financials(ticker, form)


class InsiderInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker, e.g. NVDA")
    code: Optional[str] = Field(None, description="P for open market buys only, S for sales only, empty for all")
    limit: int = Field(20, description="How many transactions, up to 50")


class InsiderTradesTool(BaseTool):
    name: str = "Insider trades"
    description: str = ("Latest Form 4 insider transactions for a company: who traded, their role, buy or sell, shares, "
                        "price, value and whether it was under a 10b5-1 plan.")
    args_schema: Type[BaseModel] = InsiderInput

    def _run(self, ticker: str, code: Optional[str] = None, limit: int = 20) -> str:
        code = (code or "").strip().upper()[:1] or None
        return core.insider_trades(ticker, code if code in ("P", "S") else None, limit)


class EightKInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker, e.g. NVDA")
    limit: int = Field(10, description="How many reports, up to 50")


class RecentEightKTool(BaseTool):
    name: str = "Recent 8-K reports"
    description: str = ("The company's latest 8-K current reports and what each one covers (earnings releases, material "
                        "agreements, leadership changes, other events), with links.")
    args_schema: Type[BaseModel] = EightKInput

    def _run(self, ticker: str, limit: int = 10) -> str:
        return core.recent_8k(ticker, limit)


def all_tools():
    return [SearchTenKTool(), SearchTenQTool(), FinancialStatementsTool(), InsiderTradesTool(), RecentEightKTool()]
