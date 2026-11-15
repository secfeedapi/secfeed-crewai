"""SEC EDGAR tools for CrewAI agents, powered by the SecFeed API (https://secfeedapi.com)."""
__version__ = "0.1.0"

try:
    from .tools import (FinancialStatementsTool, InsiderTradesTool, RecentEightKTool, SearchTenKTool,  # noqa: F401
                        SearchTenQTool, all_tools)
except ImportError:  # crewai not installed: the plain functions in secfeed_crewai.core still work
    pass
