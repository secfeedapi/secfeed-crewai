# SEC filing tools for CrewAI

Give your CrewAI agents SEC EDGAR data: 10-K and 10-Q sections, XBRL financial statements, Form 4 insider trades and 8-K reports. Powered by the [SecFeed API](https://secfeedapi.com).

No vector store, no embeddings and no OpenAI key needed for the tools: SecFeed returns the exact filing section (Risk Factors, MD&A, Business), and the tool hands your agent the paragraphs that match its question.

```bash
pip install secfeed-crewai
export SECFEED_API_KEY=sf_...   # free key: https://secfeedapi.com/signup/
```

```python
from crewai import Agent
from secfeed_crewai import SearchTenKTool, FinancialStatementsTool, InsiderTradesTool

analyst = Agent(
    role="Equity analyst",
    goal="Explain NVDA's risks and financial health from its filings",
    backstory="You only trust primary sources.",
    tools=[SearchTenKTool(), FinancialStatementsTool(), InsiderTradesTool()],
)
```

## Tools

| Tool | What the agent gets | API calls |
|---|---|---|
| `SearchTenKTool` | The paragraphs of the latest 10-K that answer a question, from the right section (Business, Risk Factors, MD&A, Market Risk), with the filing link | 2 |
| `SearchTenQTool` | Same for the latest 10-Q | 2 |
| `FinancialStatementsTool` | Income statement, balance sheet and cash flow from XBRL, last periods side by side | 1 |
| `InsiderTradesTool` | Latest Form 4 trades: who, role, buy or sell, shares, price, value, 10b5-1 flag | 1 |
| `RecentEightKTool` | Latest 8-K reports and the items each one covers, with links | 2 |

`all_tools()` returns all five. The plain functions behind them live in `secfeed_crewai.core` and work without CrewAI (LangChain, LlamaIndex, plain scripts).

Example output of `InsiderTradesTool` for MSFT:

```
MSFT insider transactions (3817 on file, latest 3):
- 2026-11-10 ... (EVP, Chief Marketing Officer): open market sale 5.00K sh @ 531.0 = $2.65M
- 2026-11-09 ... (EVP, Chief Financial Officer): open market sale 5.91K sh @ 544.2359 = $3.22M, 10b5-1 plan
```

## Example: stock research crew

`examples/stock_analysis/main.py` runs three agents (filings researcher, financial analyst, memo writer) and writes `memo-<TICKER>.md`:

```bash
export OPENAI_API_KEY=...        # or any model CrewAI supports:
export MODEL=gpt-4o-mini         # e.g. MODEL=anthropic/<model> or MODEL=openrouter/<model>
python examples/stock_analysis/main.py NVDA
```

A full run makes about a dozen SecFeed calls (tested: 11 for AMD), so the free trial covers it.

## Coming from the CrewAI stock analysis example?

The classic CrewAI stock analysis example looks up the latest filing, downloads the whole HTML page, splits it into chunks and embeds them with OpenAI to answer a question. These tools replace that whole file:

```python
# before
from tools.sec_tools import SECTools
tools = [SECTools.search_10q, SECTools.search_10k]

# after
from secfeed_crewai import SearchTenQTool, SearchTenKTool
tools = [SearchTenQTool(), SearchTenKTool()]
```

You drop `unstructured`, `faiss` and the embeddings call, and the agent reads the actual section instead of random chunks of the page.

## Also available

- [secfeed](https://pypi.org/project/secfeed/) Python and Node SDKs for every SecFeed endpoint (13F holdings, Form D, full text search, XBRL frames and more)
- [SecFeed MCP server](https://secfeedapi.com/mcp/) for Claude, Cursor and other MCP clients

## License

MIT
