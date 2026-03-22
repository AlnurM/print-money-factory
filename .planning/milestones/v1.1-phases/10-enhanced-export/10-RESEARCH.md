# Phase 10: Enhanced Export - Research

**Researched:** 2026-03-23
**Domain:** Trading bot deployment guides -- platform-specific live trading instructions
**Confidence:** HIGH

## Summary

Phase 10 adds a single new export file (`bot-building-guide.md`) to the existing 7-file export package in `/brrr:verify --approved`. The guide provides platform-specific, step-by-step instructions for deploying an approved strategy to live trading. Platform is auto-detected from the asset class in STRATEGY.md.

This is a content-generation task, not a code-engineering task. The implementation follows the exact same pattern as the existing `trading-rules.md` and `live-checklist.md` exports: read strategy context, generate AI-authored markdown, write to `.pmf/output/`. The primary research need is understanding what content belongs in each guide section across three platform categories (crypto exchanges, stock brokers, forex platforms).

**Primary recommendation:** Add a new step 5a.8 (renumber current 5a.8 to 5a.9) in `workflows/verify.md` that generates `bot-building-guide.md` following the same AI-generation pattern as steps 5a.3 and 5a.6. The guide template should contain platform-specific sections with code-pattern-level snippets (not full bots) and reference actual parameters from `phase_N_best_result.json`.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Guide has 7 sections in fixed order: Prerequisites, Platform Setup, Strategy Configuration, Order Types & Execution, Risk Management, Monitoring & Alerts, Go-Live Checklist
- **D-02:** Each section includes concrete examples with actual strategy parameters from `phase_N_best_result.json` (not generic placeholders)
- **D-03:** Code snippets at "pattern" level -- showing API call structure, not a full runnable bot
- **D-04:** Platform detected from asset class in STRATEGY.md: crypto -> exchange API (ccxt), stocks -> broker API (Alpaca/IBKR), forex -> MT5/OANDA
- **D-05:** AI reads STRATEGY.md to detect asset class automatically, no user prompt needed
- **D-06:** Ambiguous asset class -> include sections for each applicable platform
- **D-07:** Target audience: experienced trader who knows their platform but hasn't automated this specific strategy before
- **D-08:** Direct, second-person language. No hedging or disclaimers beyond standard risk warning
- **D-09:** Standard risk warning at top: "This guide assumes you've validated the strategy in backtesting. Past performance does not guarantee future results. Start with paper trading or minimal position sizes."

### Claude's Discretion
- Exact code snippet examples for each platform
- Whether to reference existing PineScript exports for TradingView-based automation
- Level of detail in the monitoring section
- Whether to include a "Common Pitfalls" subsection

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EXPT-08 | `/brrr:verify --approved` generates a `bot-building-guide.md` with platform-specific step-by-step instructions for going live | Platform API patterns documented below, integration point identified in verify.md Step 5a, guide structure defined in CONTEXT.md decisions |

</phase_requirements>

## Standard Stack

No new libraries are needed. This phase generates a markdown file using AI-authored content -- the same pattern as all other exports. The guide references platform libraries the user would install separately (ccxt, alpaca-trade-api, oandapyV20, ib_insync/ib_async), but these are NOT project dependencies.

### Libraries Referenced in Guide Content (NOT project deps)

| Library | Purpose | Platform | Guide References |
|---------|---------|----------|------------------|
| ccxt | Exchange API access | Crypto | Already a project dep for data fetching |
| alpaca-trade-api | Broker API access | Stocks | User installs separately |
| ib_insync / ib_async | IBKR API access | Stocks | User installs separately. Note: ib_insync archived (creator deceased), ib_async is active fork |
| oandapyV20 | Forex API access | Forex | User installs separately |
| v20 (official OANDA) | Forex API access | Forex | Alternative to oandapyV20, official OANDA package |
| MetaTrader5 | MT5 API access | Forex | User installs separately, Windows only |

## Architecture Patterns

### Integration Point

The bot-building guide slots into the existing export pipeline in `workflows/verify.md`:

```
Current Step 5a flow:
  5a.1: Create output directory
  5a.2: Generate PineScript files (EXPT-01)
  5a.3: Generate trading-rules.md (EXPT-02)
  5a.4: Generate performance-report.md (EXPT-03)
  5a.5: Generate backtest_final.py (EXPT-04)
  5a.6: Generate live-checklist.md (EXPT-05)
  5a.7: Copy report HTML (EXPT-06)
  5a.8: Display export summary (EXPT-07)  <-- renumber to 5a.9

New:
  5a.8: Generate bot-building-guide.md (EXPT-08)  <-- insert here
  5a.9: Display export summary (EXPT-07)  <-- update count from 7 to 8
```

### Generation Pattern (mirrors trading-rules.md)

The AI reads context, then writes the file. Same pattern used for all exports:

```
Read context:
  - .pmf/STRATEGY.md (asset class, timeframe, exchange/source)
  - .pmf/phases/phase_N_discuss.md (strategy logic details)
  - .pmf/phases/phase_N_best_result.json (optimized parameter values)
  - .pmf/output/trading-rules.md (cross-reference entry/exit rules)

Detect platform:
  - Parse asset from STRATEGY.md
  - Crypto indicators: BTC, ETH, SOL, BNB, etc. or exchange names (Binance, Bybit, Coinbase)
  - Stock indicators: SPY, AAPL, TSLA, QQQ, etc. or broker names (Alpaca, IBKR)
  - Forex indicators: EUR/USD, GBP/JPY, etc. or "forex" in strategy type

Write: .pmf/output/bot-building-guide.md
```

### Asset Class Detection Logic

```
IF asset contains "/" AND both parts are 3-4 letter currency codes (e.g., BTC/USDT, ETH/BTC):
  -> Crypto (exchange API guide)
ELIF asset contains "/" AND parts match forex pairs (e.g., EUR/USD, GBP/JPY):
  -> Forex (MT5/OANDA guide)
ELIF asset is a ticker symbol (e.g., SPY, AAPL, MSFT):
  -> Stocks (broker API guide)
ELIF Exchange/Source field mentions a crypto exchange:
  -> Crypto
ELIF Exchange/Source field mentions yfinance or a stock broker:
  -> Stocks
ELSE:
  -> Ambiguous: include brief sections for all three
```

## Platform-Specific Content Guide

### Crypto Platforms (ccxt / Exchange API)

**Prerequisites:**
- Exchange account with API key (trade-only permissions, NO withdrawal)
- ccxt installed (`pip install ccxt`)
- Paper/testnet trading enabled (Binance testnet, Bybit testnet)

**Key API Patterns:**

```python
# Connection pattern
import ccxt
exchange = ccxt.binance({
    'apiKey': os.environ['EXCHANGE_API_KEY'],
    'secret': os.environ['EXCHANGE_SECRET'],
    'enableRateLimit': True,  # Critical: prevents API bans
    'options': {'defaultType': 'spot'},  # or 'future' for derivatives
})

# Fetch current price
ticker = exchange.fetch_ticker('BTC/USDT')
current_price = ticker['last']

# Place limit order
order = exchange.create_limit_buy_order('BTC/USDT', amount, price)

# Place market order
order = exchange.create_market_buy_order('BTC/USDT', amount)

# Check open orders
open_orders = exchange.fetch_open_orders('BTC/USDT')

# Cancel order
exchange.cancel_order(order_id, 'BTC/USDT')
```

**Order Types:**
- Market orders: immediate fill, slippage risk on low-liquidity pairs
- Limit orders: price control, may not fill in fast markets
- Stop-limit orders: `exchange.create_order('BTC/USDT', 'stop_limit', 'sell', amount, price, params={'stopPrice': stop_price})`
- Exchange-specific params vary -- always check `exchange.has` dictionary

**Position Sizing:**
```python
account_balance = exchange.fetch_balance()['USDT']['free']
risk_per_trade = 0.01  # 1% risk
position_size = (account_balance * risk_per_trade) / abs(entry_price - stop_price)
```

**Rate Limiting:** ccxt handles this automatically with `enableRateLimit: True`. Never disable it. Typical limits: 1200 requests/minute (Binance), 100 requests/5 seconds (Bybit).

### Stock Platforms (Alpaca / Interactive Brokers)

**Alpaca Prerequisites:**
- Alpaca account (paper trading available immediately, no funding required)
- API key from dashboard (alpaca.markets)
- `pip install alpaca-trade-api`

**Alpaca API Patterns:**

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

client = TradingClient(
    os.environ['ALPACA_API_KEY'],
    os.environ['ALPACA_SECRET_KEY'],
    paper=True  # Set False for live trading
)

# Market order
market_order = MarketOrderRequest(
    symbol='SPY',
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)
order = client.submit_order(market_order)

# Limit order
limit_order = LimitOrderRequest(
    symbol='SPY',
    qty=10,
    side=OrderSide.BUY,
    limit_price=450.00,
    time_in_force=TimeInForce.GTC
)
order = client.submit_order(limit_order)

# Get account info
account = client.get_account()
buying_power = float(account.buying_power)
```

**IBKR Prerequisites:**
- Interactive Brokers account with paper trading enabled
- TWS (Trader Workstation) or IB Gateway running locally
- API enabled in TWS settings (Edit -> Global Configuration -> API -> Settings)
- Port 7497 for paper, 7496 for live
- `pip install ib_async` (NOT ib_insync -- archived, creator deceased)

**IBKR API Patterns:**

```python
from ib_async import IB, Stock, MarketOrder, LimitOrder

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # 7497=paper, 7496=live

contract = Stock('SPY', 'SMART', 'USD')
ib.qualifyContracts(contract)

# Market order
order = MarketOrder('BUY', 10)
trade = ib.placeOrder(contract, order)

# Limit order
order = LimitOrder('BUY', 10, 450.00)
trade = ib.placeOrder(contract, order)

# Account summary
account_values = ib.accountSummary()
```

**Key Differences:**
- Alpaca: REST API, always available, US stocks + crypto, no software to run
- IBKR: Requires TWS/Gateway running, global markets, more complex but more powerful
- Both support paper trading with identical API to live

### Forex Platforms (OANDA / MT5)

**OANDA Prerequisites:**
- OANDA fxTrade account (practice account available free)
- API token from Account Management Portal -> My Services -> Manage API Access
- `pip install oandapyV20`

**OANDA API Patterns:**

```python
import oandapyV20
from oandapyV20.endpoints import orders, accounts, trades
from oandapyV20.contrib.requests import MarketOrderRequest

client = oandapyV20.API(
    access_token=os.environ['OANDA_TOKEN'],
    environment='practice'  # or 'live'
)
account_id = os.environ['OANDA_ACCOUNT_ID']

# Market order
order_data = MarketOrderRequest(
    instrument='EUR_USD',  # Note: underscore, not slash
    units=10000,  # Positive=buy, negative=sell
    stopLossOnFill={"price": "1.0800"},
    takeProfitOnFill={"price": "1.1200"}
)
r = orders.OrderCreate(account_id, data=order_data.data)
client.request(r)

# Get account summary
r = accounts.AccountSummary(account_id)
client.request(r)
balance = float(r.response['account']['balance'])
```

**MT5 Prerequisites:**
- MetaTrader 5 terminal installed (Windows only, or Wine on Mac/Linux)
- Broker account with MT5 support
- `pip install MetaTrader5` (Windows only)
- Note: MT5 Python integration only works on Windows. For Mac/Linux users, recommend OANDA instead

**MT5 API Patterns:**

```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(login=12345, password='password', server='BrokerServer')

# Market order
request = {
    'action': mt5.TRADE_ACTION_DEAL,
    'symbol': 'EURUSD',
    'volume': 0.1,  # Lots
    'type': mt5.ORDER_TYPE_BUY,
    'price': mt5.symbol_info_tick('EURUSD').ask,
    'sl': 1.0800,  # Stop loss
    'tp': 1.1200,  # Take profit
    'deviation': 10,  # Max slippage in points
    'magic': 234000,  # EA magic number
    'comment': 'strategy_name',
}
result = mt5.order_send(request)
```

**Key Differences:**
- OANDA: REST API, cross-platform, practice accounts free, limited to OANDA's instruments
- MT5: Windows-only Python lib, connects to any MT5 broker, wider instrument selection, more complex setup

## Risk Management Controls (All Platforms)

Every bot-building guide MUST include these risk controls regardless of platform:

### Position Sizing Rules
- **Fixed percentage risk:** Never risk more than 1-2% of account on a single trade
- **Formula:** `position_size = (account_balance * risk_pct) / abs(entry_price - stop_loss_price)`
- **Use actual strategy stop loss** from best_result.json parameters

### Circuit Breakers
- **Daily loss limit:** Stop trading after 3-5% account drawdown in a single day
- **Consecutive loss limit:** Pause after N consecutive losses (recommend 5)
- **Maximum drawdown:** Kill switch if account drops X% from peak (use strategy's max drawdown from backtest as reference)

### Slippage Handling
- **Limit orders preferred** for entries when the strategy's timeframe allows (4H+)
- **Market orders acceptable** for fast timeframes (1M-15M) where fill speed matters more than exact price
- **Slippage budget:** Expect 0.01-0.05% for liquid pairs, 0.1-0.5% for illiquid pairs
- **Adjust position size** to account for expected slippage vs backtest assumptions

### API Key Security
- Store keys in environment variables, NEVER hardcode
- Use trade-only permissions (no withdrawal capability)
- IP-whitelist API keys where supported (Binance, Bybit)
- Use separate API keys for paper and live trading

## Monitoring & Alerting Patterns

### What to Monitor
1. **Trade execution:** Did the order fill at expected price? Check slippage per trade
2. **Position status:** Are stops and targets properly placed after entry?
3. **Account equity:** Real-time P&L tracking, drawdown from peak
4. **API health:** Connection status, rate limit usage, error frequency
5. **Strategy drift:** Compare live win rate / avg trade to backtest metrics after 30+ trades

### Alerting Options (by complexity)
- **Simple:** Python logging to file + periodic manual review
- **Medium:** Telegram bot notifications via `python-telegram-bot` or Discord webhooks
- **Advanced:** PagerDuty / email alerts for critical events (circuit breaker triggered, API errors)

### When to Intervene
- API connection lost for >5 minutes during active position
- Slippage exceeds 2x expected on consecutive trades
- Live metrics diverge >20% from backtest after 30+ trades
- Circuit breaker triggers -- do NOT override, investigate first

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Platform API wrappers | Custom HTTP clients for each exchange/broker | ccxt (crypto), alpaca-trade-api (stocks), oandapyV20 (forex) | Authentication, rate limiting, error handling are deceptively complex |
| Full runnable bot code | Complete bot in the guide | Code patterns + references to open-source bot frameworks | Out of scope per project constraints. Guide stays at pattern level |
| Monitoring dashboard | Custom monitoring UI | Existing tools: Telegram bots, Discord webhooks, exchange mobile apps | The guide recommends monitoring approaches, doesn't build them |

## Common Pitfalls

### Pitfall 1: Guide becomes a full bot tutorial
**What goes wrong:** The guide grows into a comprehensive bot-building tutorial rather than a deployment reference
**Why it happens:** Each platform has many edge cases, and it's tempting to cover them all
**How to avoid:** Enforce D-03 strictly: code snippets show API call structure only. Link to platform documentation for comprehensive guides. Target audience already knows their platform (D-07)
**Warning signs:** Any code block longer than 15 lines; sections explaining what an API key is

### Pitfall 2: Generic placeholders instead of strategy parameters
**What goes wrong:** Guide uses `{YOUR_STOP_LOSS}` instead of the actual optimized value
**Why it happens:** Writer forgets to read `best_result.json` and defaults to template-style writing
**How to avoid:** D-02 requires concrete examples with actual strategy parameters. The workflow step must explicitly read `phase_N_best_result.json` and inject values into examples
**Warning signs:** Any `{placeholder}` that could be replaced with a real number from the backtest

### Pitfall 3: Wrong platform for the asset class
**What goes wrong:** Guide suggests Alpaca for crypto or ccxt for stocks
**Why it happens:** Asset class detection fails or is skipped
**How to avoid:** Detection logic must parse STRATEGY.md before generating content. The crypto/stock/forex distinction is the first decision point
**Warning signs:** Platform and asset class mismatch in generated content

### Pitfall 4: Outdated library references
**What goes wrong:** Guide recommends ib_insync (archived) or deprecated OANDA v1 API
**Why it happens:** Training data may be stale for rapidly evolving libraries
**How to avoid:** Use the library names documented in this research. ib_insync -> ib_async. OANDA v1 -> v20 API
**Warning signs:** Import statements for deprecated packages

### Pitfall 5: Missing risk warning
**What goes wrong:** Guide goes straight into API setup without the required disclaimer
**Why it happens:** D-09 specifies a risk warning at the top but it's easy to forget in generation
**How to avoid:** The workflow step template must start with the risk warning as the first content block
**Warning signs:** Guide starts with "Prerequisites" instead of the risk warning

## Code Examples

### Verify Workflow Step Template (5a.8)

The new step in `workflows/verify.md` should follow this structure:

```markdown
### 5a.8: Generate bot-building-guide.md (EXPT-08)

Read strategy context:

- `.pmf/STRATEGY.md` for asset class, exchange/source, timeframe
- `.pmf/phases/phase_N_discuss.md` for strategy logic details
- `.pmf/phases/phase_N_best_result.json` for optimized parameter values
- `.pmf/output/trading-rules.md` for cross-reference with entry/exit rules

Detect platform from STRATEGY.md:
- Crypto assets (BTC, ETH, pairs with USDT/BTC) -> Exchange API section (ccxt)
- Stock assets (ticker symbols like SPY, AAPL) -> Broker API section (Alpaca, IBKR)
- Forex assets (pairs like EUR/USD, GBP/JPY) -> MT5/OANDA section
- Ambiguous -> Include brief sections for all applicable platforms

Write `.pmf/output/bot-building-guide.md`:
```

### Guide Output Template

```markdown
# Bot Building Guide: {strategy_name}

> **Risk Warning:** This guide assumes you've validated the strategy in backtesting.
> Past performance does not guarantee future results. Start with paper trading
> or minimal position sizes.

## 1. Prerequisites

{Platform-specific prerequisites based on detected asset class}

## 2. Platform Setup

{Step-by-step API setup for the detected platform}
{Code pattern showing connection/authentication}

## 3. Strategy Configuration

{Map best_result.json parameters to platform configuration}
{Show how each parameter translates to live trading settings}

## 4. Order Types & Execution

{Which order types to use for this strategy's entry/exit style}
{Slippage handling based on timeframe and asset liquidity}

## 5. Risk Management

{Position sizing formula with actual parameters}
{Circuit breaker rules}
{Maximum exposure limits}

## 6. Monitoring & Alerts

{What to watch}
{Alerting setup recommendations}
{When to intervene vs stay hands-off}

## 7. Go-Live Checklist

{Strategy-specific pre-launch verification}
{Distinct from generic live-checklist.md}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ib_insync for IBKR | ib_async (active fork) | 2024 (creator deceased) | Guide must recommend ib_async, not ib_insync |
| OANDA REST v1 API | OANDA REST v20 API | 2018+ | v1 fully deprecated. Only reference v20 endpoints |
| alpaca-trade-api (old SDK) | alpaca-py (new SDK) | 2023+ | Both work but alpaca-py is the current recommended SDK |
| MetaTrader 4 | MetaTrader 5 | Ongoing | MT5 has Python integration; MT4 does not |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual validation (no automated test framework in project) |
| Config file | none |
| Quick run command | Manual: run `/brrr:verify --approved` on a test strategy |
| Full suite command | Manual: verify export generates 8 files including bot-building-guide.md |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXPT-08 | bot-building-guide.md generated with platform-specific content | manual-only | Run `/brrr:verify --approved` and inspect output | N/A |

**Manual-only justification:** This phase modifies a Claude Code workflow (markdown prompt). The "test" is running the workflow and inspecting the generated markdown output. There is no Python code to unit-test -- the entire implementation is AI-generated content triggered by workflow instructions.

### Sampling Rate
- **Per task commit:** Manual review of verify.md changes for correctness
- **Per wave merge:** Run `/brrr:verify --approved` on a sample strategy
- **Phase gate:** Verify 8-file export package with bot-building-guide.md present and containing platform-specific content

### Wave 0 Gaps
None -- no test infrastructure needed. This phase modifies a workflow markdown file.

## Open Questions

1. **PineScript cross-reference (Claude's discretion)**
   - What we know: The export already generates PineScript files. TradingView supports webhook-based automation
   - What's unclear: Whether the bot-building guide should mention "use TradingView alerts + webhook to trigger orders" as an alternative to direct API integration
   - Recommendation: Include a brief note in the guide: "For TradingView-based automation, use the exported PineScript indicator with TradingView alerts connected to your broker's webhook endpoint." One paragraph, not a full section

2. **Common Pitfalls subsection (Claude's discretion)**
   - What we know: Live trading has well-documented gotchas per platform
   - What's unclear: Whether a dedicated subsection adds value or duplicates live-checklist.md
   - Recommendation: Include 3-4 platform-specific pitfalls inline within the relevant sections (e.g., "OANDA uses underscores not slashes: EUR_USD not EUR/USD") rather than a separate subsection. Keeps the guide focused

3. **Monitoring detail level (Claude's discretion)**
   - What we know: Monitoring ranges from simple logging to full alerting infrastructure
   - What's unclear: How much monitoring setup to include vs just listing what to monitor
   - Recommendation: Show a minimal Telegram/Discord webhook notification pattern (5-10 lines) as a concrete example, then list what to monitor. The target audience (D-07) can build from there

## Sources

### Primary (HIGH confidence)
- `workflows/verify.md` Steps 5a.1-5a.8 -- existing export pipeline pattern
- `workflows/verify.md` Step 5a.3 -- trading-rules.md generation (tone model)
- `workflows/verify.md` Step 5a.6 -- live-checklist.md generation (related content)
- `.planning/research/FEATURES.md` -- Bot-building guide feature specification
- `10-CONTEXT.md` -- All locked decisions D-01 through D-09

### Secondary (MEDIUM confidence)
- [OANDA REST v20 API docs](https://developer.oanda.com/rest-live-v20/introduction/) -- OANDA endpoint patterns
- [Alpaca Learn: Algorithmic Trading in Python](https://alpaca.markets/learn/algorithmic-trading-python-alpaca) -- Alpaca API patterns
- [IBKR Python API Guide](https://www.interactivebrokers.com/campus/ibkr-quant-news/interactive-brokers-python-api-native-a-step-by-step-guide/) -- IBKR setup steps
- [ccxt GitHub](https://github.com/ccxt/ccxt) -- Exchange API unification
- [oandapyV20 PyPI](https://pypi.org/project/oandapyV20/) -- OANDA Python wrapper
- [ib_insync GitHub (archived)](https://github.com/erdewit/ib_insync) -- Note on ib_async fork

### Tertiary (LOW confidence)
- Risk management circuit breaker thresholds (3-5% daily, 1-2% per trade) -- sourced from multiple trading bot guides, community consensus rather than formal standard

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries to add; this is a content generation task
- Architecture: HIGH -- integration point is clear (verify.md Step 5a), pattern mirrors existing exports exactly
- Pitfalls: HIGH -- well-understood domain; the main risks are content quality issues, not technical ones
- Platform API patterns: MEDIUM -- based on web search verification of current library status; API patterns are standard but specific method signatures should be verified against latest docs at implementation time

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (stable domain -- platform APIs change slowly)
