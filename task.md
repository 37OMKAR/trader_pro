# MARKET AI — INDIAN MARKET AUTONOMOUS RESEARCH, PREDICTION & PAPER-TRADING PLATFORM

## 0. PROJECT MISSION

Build a production-grade, India-first AI market intelligence platform focused primarily on:

* NSE
* BSE
* NIFTY family
* SENSEX
* BANK NIFTY
* FINNIFTY
* Indian equities
* Indian futures
* Indian options
* Indian market breadth
* Indian sector intelligence
* FII/DII activity
* Indian corporate events
* Indian macroeconomic events

The platform must combine:

1. Indian market data
2. Quantitative analysis
3. Machine-learning prediction
4. Strategy generation
5. Historical backtesting
6. Dummy-money/paper trading
7. Automated strategy evaluation
8. Strategy ranking
9. Agent-driven strategy iteration
10. Hermes agent orchestration
11. Tavily/web research
12. Telegram alerts
13. WhatsApp alerts
14. Futuristic financial dashboard
15. User-uploaded-image talking avatar
16. Local/offline TTS
17. Optional cloud TTS
18. AI teaching/explanation
19. Portfolio intelligence
20. Risk management
21. Model/strategy versioning
22. Full auditability

PRIMARY PRINCIPLE:

THE MARKET ENGINE IS THE SOURCE OF TRUTH.

Hermes is the agent/orchestration layer.

The quantitative engine calculates signals and probabilities.

The strategy engine executes explicit rules.

The paper-trading engine records simulated trades.

The ranking engine evaluates strategies.

The LLM explains, researches, designs, critiques and coordinates.

The LLM must NOT fabricate market data, performance statistics, probabilities, returns or trade history.

============================================================

1. CORE ARCHITECTURE
   ============================================================

Build as a modular monorepo.

market-ai/

apps/
web/
api/

services/
market-data/
market-calendar/
feature-engine/
prediction-engine/
strategy-engine/
backtest-engine/
paper-trading-engine/
portfolio-engine/
risk-engine/
alert-engine/
research-engine/
notification-engine/
avatar-engine/
tts-engine/
model-registry/
strategy-registry/

agents/
supervisor/
market-agent/
technical-agent/
fundamental-agent/
fno-agent/
macro-agent/
news-agent/
prediction-agent/
strategy-builder-agent/
strategy-critic-agent/
strategy-research-agent/
portfolio-agent/
risk-agent/
teacher-agent/
avatar-director-agent/

mcp/
market-mcp/
feature-mcp/
prediction-mcp/
strategy-mcp/
backtest-mcp/
papertrade-mcp/
portfolio-mcp/
risk-mcp/
research-mcp/
alert-mcp/
avatar-mcp/

models/
prediction/
embeddings/
avatar/
tts/

data/
raw/
normalized/
features/
backtests/
paper-trades/

packages/
shared-types/
event-schema/
validation/
logging/
ui/

infra/
docker/
postgres/
redis/
object-storage/
monitoring/

docs/
architecture/
strategy-engine/
prediction-engine/
paper-trading/
agents/
avatar/
deployment/
security/

============================================================
2. API-FIRST ARCHITECTURE
=========================

All significant external calls MUST pass through provider abstractions.

The application must NOT directly scatter API calls throughout business logic.

Create interfaces:

MarketDataProvider
NewsProvider
ResearchProvider
MacroDataProvider
BrokerProvider
LLMProvider
TTSProvider
MessagingProvider

All production data access must flow through these interfaces.

Examples:

MarketDataProvider:
get_quote()
get_history()
get_index()
get_options_chain()
get_fii_dii()
get_market_breadth()

ResearchProvider:
search()
fetch()
company_research()

TTSProvider:
synthesize()
stream()
list_voices()

MessagingProvider:
send_text()
send_voice()
send_image()

The provider implementation must be replaceable without changing strategy code.

============================================================
3. API CALL POLICY
==================

Use APIs wherever strong/current/external information is required.

Examples:

* live market data
* current quotes
* current news
* research
* broker/provider data
* current corporate announcements
* current F&O data

Do NOT call an LLM merely to retrieve numerical market data.

Example:

WRONG:
LLM -> "What is NIFTY today?"

CORRECT:
MarketDataProvider -> exact quote
Hermes -> explains quote

All numerical values displayed to the user must originate from a structured data source.

Every external data result must carry:

provider
timestamp
source
request_id
data_timestamp
retrieved_at

============================================================
4. INDIA-FIRST MARKET DATA
==========================

Build the initial universe around Indian instruments.

Priority:

1. NIFTY 50
2. BANK NIFTY
3. SENSEX
4. FINNIFTY
5. NIFTY sector indices
6. NIFTY 100
7. NIFTY 250
8. liquid NSE equities
9. stock futures
10. stock options
11. index futures
12. index options

Do not begin with global equities.

Global data is only an input to Indian market context.

Example global inputs:

S&P 500
NASDAQ
Dow
US 10Y
USDINR
Brent crude
Gold
Asian markets

Treat these as market-context features for India.

============================================================
5. MARKET DATA DATABASE
=======================

Use PostgreSQL.

Use TimescaleDB or ClickHouse for high-volume time series if justified.

Use Redis for:

* real-time events
* caches
* queues
* sessions

Core market tables:

symbols
exchanges
indices
index_components
quotes
candles
ticks
corporate_actions
trading_calendars
market_holidays
market_status
sectors
fii_dii
breadth
futures
options
option_chain_snapshots
open_interest
participant_oi
events
news

Canonical symbol identity must not depend only on ticker.

Store:

exchange
symbol
ISIN
company_name
instrument_type
series
sector
industry
expiry
strike
option_type
lot_size
tick_size
active

============================================================
6. DATA LICENSING ARCHITECTURE
==============================

Never assume scraped market data is suitable for commercial redistribution.

Create provider adapters.

Development:
DevelopmentMarketDataProvider

Production:
LicensedMarketDataProvider

Optional:
BrokerMarketDataProvider

Keep raw source data separate from normalized internal data.

Every dataset stores:

source
license_type
retrieved_at
effective_at
permission_class

Do not build the platform around an undocumented scraping dependency.

============================================================
7. INDIAN MARKET CALENDAR
=========================

Create exchange-aware calendars.

Support:

market_open
market_close
pre_open
post_close
weekends
exchange holidays
special sessions
expiry dates
result dates
corporate event dates

Never assume generic Monday-Friday 24/7 operation.

All schedules use Asia/Kolkata as the primary Indian-market timezone.

============================================================
8. FUTURISTIC DASHBOARD
=======================

Design the UI as a modern institutional-grade financial intelligence terminal.

Visual direction:

* dark premium interface
* glass/metal panels
* subtle gradients
* strong data hierarchy
* restrained animation
* real-time status indicators
* large financial numerals
* dense but readable information
* futuristic without becoming decorative
* responsive
* desktop-first
* tablet compatible

DO NOT make the dashboard look like a generic SaaS admin panel.

Main navigation:

MARKET
Overview
India Market
Indices
Sectors
Stocks
F&O
Heatmap

AI
Predictions
Signals
Research
Strategy Lab
Strategy Rankings
Agent Activity

PORTFOLIO
Paper Portfolio
Live Portfolio placeholder
Risk
Attribution
Positions

INTELLIGENCE
News
Corporate Events
FII/DII
Macro
Market Regime

LAB
Backtesting
Dummy Trading
Strategy Builder
Strategy Evolution
Model Performance

LEARN
AI Tutor
Explain Chart
Explain Stock
Explain Strategy

SETTINGS
Data Providers
Models
Alerts
Messaging
Avatar
API Keys

============================================================
9. MAIN MARKET SCREEN
=====================

Top bar:

market status
IST clock
NIFTY
SENSEX
BANK NIFTY
INDIA VIX
FII/DII

Primary panels:

Market Regime
Market Breadth
Sector Rotation
Top AI Signals
Biggest Movers
F&O Positioning
News Intelligence

Main chart:

NIFTY / selected stock

Secondary:

Prediction probability
Expected movement
Risk score
Model drivers

============================================================
10. FUTURES DASHBOARD
=====================

Create a dedicated FUTURES & DERIVATIVES dashboard.

Sections:

INDEX FUTURES
STOCK FUTURES
OPTIONS
OPEN INTEREST
IV
PCR
OI CHANGE
BASIS
ROLLOVER
EXPIRY

For each contract show:

symbol
expiry
spot
futures price
basis
volume
open interest
OI change
IV where applicable
PCR where applicable

Visualization:

OI build-up
long build-up
short build-up
long unwinding
short covering

Use explicit deterministic calculations.

Never ask the LLM to infer arithmetic from screenshots.

============================================================
11. OPTIONS ANALYTICS
=====================

Build:

strike ladder
call OI
put OI
change OI
volume
IV
delta
gamma
theta
vega where data permits

Derived:

PCR
OI concentration
support zones
resistance zones
IV regime
expiry concentration

The options engine must return structured data.

Hermes explains the result afterward.

============================================================
12. MARKET REGIME ENGINE
========================

Build a dedicated Indian Market Regime Engine.

States:

BULL
BEAR
RANGE
HIGH_VOLATILITY
LOW_VOLATILITY
RISK_ON
RISK_OFF
TRANSITION

Inputs:

NIFTY trend
BANK NIFTY trend
breadth
India VIX
FII/DII
sector momentum
USDINR
Brent
global indices
US yields
options positioning
market volatility

Output:

regime
probability
confidence
drivers
risks

Example:

{
"regime": "BULL",
"probability": 0.72,
"confidence": 0.69,
"drivers": [...],
"risks": [...]
}

============================================================
13. FEATURE ENGINE
==================

Create reusable feature pipelines.

PRICE:

returns
gap
ATR
RSI
MACD
moving averages
volatility
momentum
breakouts
relative strength

VOLUME:

volume change
volume z-score
volume/average volume
delivery percentage

MARKET:

NIFTY return
BANK NIFTY return
India VIX
breadth
sector momentum

F&O:

OI
OI change
volume
IV
PCR
basis
expiry distance

FUNDAMENTAL:

PE
PB
ROE
ROCE
debt/equity
revenue growth
profit growth
EPS growth
margin
cash flow

EVENT:

earnings
dividend
split
bonus
buyback
management changes
major announcements

Each feature must have:

feature_name
value
effective_timestamp
source
version

============================================================
14. PREDICTION ENGINE
=====================

MVP models:

logistic model
gradient boosting
random forest if useful
factor model
ensemble

Do not begin with an unnecessarily large neural network.

Prediction horizons:

intraday if data permits
1D
5D
20D
3M

Output:

direction
probability
expected_return
confidence
risk_score

Never output a guaranteed target.

============================================================
15. PREDICTION REGISTRY
=======================

Every prediction becomes an immutable record.

Fields:

prediction_id
symbol
model_id
model_version
generated_at
data_snapshot_id
feature_snapshot_id
horizon
direction
probability
expected_return
confidence
risk_score
market_regime

Later append:

actual_return
actual_direction
error
hit
calibration_score
evaluated_at

Never overwrite historical predictions.

============================================================
16. STRATEGY LAB — CORE FEATURE
===============================

This is one of the most important parts of the platform.

Create:

STRATEGY LAB

The user must be able to:

* create a strategy
* describe a strategy in natural language
* have an agent convert it into formal rules
* inspect those rules
* backtest it
* paper-trade it
* rank it
* compare it
* clone it
* mutate it
* retire it

Example:

User:

"Create a strategy that buys large-cap Indian stocks when momentum is strong, volume confirms the move and the broader market is bullish."

Strategy Agent converts this to machine-readable rules.

Example:

ENTRY:

market_regime == BULL
AND
relative_strength > 70
AND
volume_zscore > 1
AND
RSI between 50 and 70

EXIT:

prediction_probability < 55
OR
stop_loss triggered
OR
take_profit triggered
OR
market_regime becomes BEAR

The agent must show the formalized rules before allowing them to be tested.

============================================================
17. STRATEGY DSL
================

Do not let agents write arbitrary executable Python as the strategy definition.

Create a controlled Strategy DSL.

Example:

{
"strategy_name": "India Momentum v1",
"universe": "NIFTY_100",
"timeframe": "1D",

"entry": [
{
"feature": "market_regime",
"operator": "eq",
"value": "BULL"
},
{
"feature": "relative_strength",
"operator": ">",
"value": 70
}
],

"exit": [
{
"feature": "prediction_probability",
"operator": "<",
"value": 0.55
}
],

"risk": {
"stop_loss": 0.05,
"max_position_pct": 0.10
}
}

Validate the strategy against a strict JSON schema.

The strategy runtime interprets this DSL.

============================================================
18. STRATEGY GENERATION AGENT
=============================

Create StrategyBuilderAgent.

Responsibilities:

* inspect available features
* inspect historical market behavior
* propose hypotheses
* construct Strategy DSL
* explain rationale
* specify assumptions
* specify invalidation
* request backtest

Do NOT let it directly deploy live strategies.

Required strategy specification:

name
hypothesis
universe
timeframe
entry
exit
position sizing
risk
expected behavior
known failure conditions

============================================================
19. STRATEGY CRITIC AGENT
=========================

Create StrategyCriticAgent.

After each backtest, critique:

* return
* drawdown
* volatility
* Sharpe
* Sortino
* hit rate
* profit factor
* turnover
* trade count
* stability
* regime dependency
* concentration
* overfitting
* parameter sensitivity

It must identify suspicious behavior.

Examples:

"Excellent return but only 17 trades."

"Performance disappears outside one bull regime."

"Strategy is highly sensitive to RSI threshold."

"Drawdown is too high."

"Possible overfitting."

============================================================
20. STRATEGY MUTATION AGENT
===========================

Create StrategyEvolutionAgent.

Inputs:

strategy version
backtest
paper-trading results
critic report
market regime analysis

It may propose:

parameter changes
entry changes
exit changes
filters
risk changes
universe changes
timeframe changes

Each proposal becomes a NEW immutable strategy version.

Never overwrite the parent strategy.

Example:

Strategy v1
->
Mutation A -> v1.1
Mutation B -> v1.2
Mutation C -> v1.3

All remain in the registry.

============================================================
21. STRATEGY GENETICS / EVOLUTION
=================================

Support later:

population of strategies

generation 1:
S1
S2
S3
S4

evaluate

rank

retain top candidates

mutate

generation 2:
S1.1
S1.2
S2.1
S3.1

evaluate again

This is NOT unrestricted autonomous evolution.

Every generation must record:

parent_strategy_id
mutation_reason
changed_parameters
backtest_dataset
results
ranking

============================================================
22. ANTI-OVERFITTING
====================

This is mandatory.

Backtesting must include:

train period
validation period
out-of-sample test period

Use walk-forward validation.

Never rank strategies solely on total return.

Require minimum:

trade count
data coverage
out-of-sample period
stability

Flag:

overfitting
look-ahead bias
survivorship bias
future leakage
parameter instability

Do not allow the StrategyEvolutionAgent to optimize on the final untouched test set.

============================================================
23. BACKTEST ENGINE
===================

Inputs:

strategy_id
market universe
date range
initial capital
transaction costs
slippage
position size
execution model

Outputs:

total return
CAGR
annualized volatility
Sharpe
Sortino
max drawdown
Calmar
win rate
average win
average loss
profit factor
trade count
turnover
exposure
best period
worst period

Also produce equity curve.

Store every backtest as immutable.

============================================================
24. DUMMY MONEY / PAPER TRADING
===============================

Build a dedicated PAPER TRADING LAB.

No real-money execution.

Starting virtual capital:

configurable

default:
₹10,00,000

User can choose:

₹1,00,000
₹5,00,000
₹10,00,000
₹50,00,000
custom

Paper account contains:

cash
positions
orders
fills
fees
slippage
realized P&L
unrealized P&L
margin
exposure

============================================================
25. PAPER TRADING MODES
=======================

MODE 1:
Manual paper trading

MODE 2:
Strategy-generated trades

MODE 3:
Agent-managed paper portfolio

MODE 4:
Strategy tournament

MODE 5:
Autonomous research paper trading

No live order placement in these modes.

============================================================
26. PAPER ORDER ENGINE
======================

Support:

market
limit
stop
stop-limit

Equity first.

F&O later.

Every paper order must record:

order_id
strategy_id
symbol
side
quantity
price
timestamp
execution_price
slippage
fees
reason
model_snapshot
signal_snapshot

Do not invent fills after the fact.

Use configurable execution assumptions.

============================================================
27. AGENT PAPER TRADING
=======================

Allow the StrategyBuilderAgent to deploy a new strategy into a paper account.

Flow:

Strategy created
->
backtest
->
critic
->
approval gate
->
paper deployment
->
live market observations
->
simulated trades
->
performance evaluation
->
strategy ranking

The agent may manage only paper money.

============================================================
28. STRATEGY TOURNAMENT
=======================

Create:

STRATEGY TOURNAMENT

Example:

Competition:
India Large Cap — 90 Days

Capital:
₹10,00,000 virtual

Strategies:

Momentum v1
Value v2
Breakout v4
Mean Reversion v2
AI Hybrid v3
Market Regime v5

All strategies run with identical:

starting capital
transaction costs
slippage
market universe
dates
execution assumptions

Display leaderboard.

============================================================
29. STRATEGY RANKING
====================

Do NOT rank only by return.

Create composite score:

StrategyScore =
return_score

* risk_adjusted_score
* drawdown_score
* stability_score
* robustness_score
* consistency_score

Recommended conceptual dimensions:

Return
Risk
Drawdown
Consistency
Out-of-sample performance
Trade count
Regime robustness
Parameter robustness

Weights must be configurable.

Display each component.

Example:

MOMENTUM v4

Overall:
87.4

Return:
92

Risk:
81

Drawdown:
76

Stability:
94

Out-of-sample:
89

Robustness:
91

============================================================
30. STRATEGY RANKING MUST HAVE BENCHMARKS
=========================================

Every strategy must be compared with:

Buy & Hold benchmark
NIFTY benchmark
appropriate sector benchmark

Example:

Strategy:
+21.4%

NIFTY:
+13.1%

Alpha:
+8.3%

But also:

Strategy Max DD:
-8.4%

NIFTY Max DD:
-11.2%

Do not call a strategy superior solely because it has a higher return.

============================================================
31. PAPER TRADING SCORE
=======================

Separate:

BACKTEST SCORE
and
PAPER SCORE

A strategy with excellent backtest but poor paper performance must be downgraded.

Example:

Backtest:
91

Paper:
58

Status:
DEGRADED

Reason:
Live regime changed.

============================================================
32. STRATEGY LIFECYCLE
======================

Statuses:

DRAFT
BACKTESTING
VALIDATED
PAPER_TRADING
RANKED
PROMOTED
DEGRADED
RETIRED

Never automatically promote a strategy to real trading.

============================================================
33. STRATEGY PROMOTION RULES
============================

Promotion requires deterministic gates.

Example:

minimum out-of-sample period
minimum trade count
acceptable max drawdown
acceptable stability
paper-trading performance
no critical data errors

Then:

PROMOTION CANDIDATE

requires user approval for anything beyond paper trading.

============================================================
34. STRATEGY LEARNING LOOP
==========================

The autonomous learning cycle is:

1. Observe market
2. Collect data
3. Generate hypotheses
4. Generate strategy
5. Formalize Strategy DSL
6. Validate
7. Backtest
8. Critique
9. Reject or improve
10. Paper trade
11. Observe results
12. Re-evaluate
13. Rank
14. Mutate
15. Test again
16. Retain historical versions

Pseudo workflow:

while research_budget_available:

```
hypothesis = StrategyResearchAgent.generate()

strategy = StrategyBuilderAgent.formalize(hypothesis)

validate(strategy)

backtest(strategy)

critique(strategy)

if passes_validation:
    paper_deploy(strategy)

observe(strategy)

rank(strategy)

if improvement_possible:
    generate_mutation()
```

This loop must be fully auditable.

============================================================
35. AGENT BUDGET
================

Do not allow agents to generate unlimited strategies.

Configure:

max_strategies_per_day
max_backtests_per_strategy
max_mutations
max_concurrent_backtests
max LLM calls
max API calls
max compute budget

Example development defaults:

10 new hypotheses/day
20 mutations/day
100 backtests/day

Make configurable.

============================================================
36. AGENT SPECIALIZATION
========================

Do not use one giant agent.

Use:

MarketAgent:
What is happening?

QuantAgent:
What do the numbers say?

StrategyBuilderAgent:
What rule-based strategy could exploit this?

StrategyCriticAgent:
Why might this strategy fail?

BacktestAgent:
Run the simulation.

PaperTradingAgent:
Manage dummy portfolio.

ResearchAgent:
Find supporting/refuting evidence.

RiskAgent:
Assess risk.

StrategyEvolutionAgent:
Generate improved variants.

Hermes Supervisor:
Coordinate all of them.

============================================================
37. HERMES ROLE
===============

Use Hermes as supervisor.

Current Hermes supports MCP, delegated/parallel subagents, scheduled tasks, API server capabilities and messaging destinations including Telegram and WhatsApp. Use these capabilities rather than rebuilding the orchestration layer unnecessarily.

Hermes tools should include:

market MCP
prediction MCP
strategy MCP
backtest MCP
papertrade MCP
portfolio MCP
risk MCP
research MCP
alert MCP
avatar MCP

Use narrow toolsets.

Read-only market tools may be safely parallelized.

Write-state tools must NOT be blindly parallelized.

============================================================
38. HERMES SCHEDULED JOBS
=========================

Use Hermes scheduled jobs for:

pre-market briefing
post-market review
daily strategy report
paper-trading summary
strategy ranking refresh
strategy degradation review

Use script-only scheduled jobs where no LLM reasoning is required.

Example:

"Alert me when a paper strategy's drawdown exceeds 10%."

The deterministic alert engine should detect this without an LLM.

Then Hermes can explain the event.

============================================================
39. STRATEGY RESEARCH CRON
==========================

Create daily agent workflow:

07:30 IST

Research Indian market.

Tasks:

global overnight context
Indian news
RBI
corporate events
FII/DII
options
sector rotation
candidate strategy opportunities

Produce:

research packet

Do not automatically change deployed strategy.

============================================================
40. AFTER-MARKET STRATEGY REVIEW
================================

After market close:

For each active paper strategy:

calculate:
daily P&L
drawdown
positions
new trades
signal quality
benchmark performance
risk

StrategyCriticAgent reviews.

Output:

KEEP
WATCH
DEGRADE
RETIRE

The ranking engine updates afterward.

============================================================
41. STRATEGY RANKING DASHBOARD
==============================

Create:

/strategy-ranking

Top cards:

#1 strategy
#2 strategy
#3 strategy

Leaderboard columns:

rank
strategy
status
return
CAGR
Sharpe
Sortino
max DD
win rate
profit factor
trades
out-of-sample score
paper score
overall score

Filters:

1D
1M
3M
6M
1Y
3Y

Market regimes:

bull
bear
range
high volatility

============================================================
42. STRATEGY EVOLUTION GRAPH
============================

Create visual family tree:

Momentum v1
├── Momentum v1.1
│     ├── v1.1.1
│     └── v1.1.2
└── Momentum v1.2

Each node shows:

score
return
drawdown
status

This makes agent evolution transparent.

============================================================
43. STRATEGY COMPARISON
=======================

User can select up to 5 strategies.

Compare:

return
risk
drawdown
Sharpe
Sortino
trade count
stability
benchmark alpha
paper performance

Charts:

equity curves
drawdowns
monthly returns
regime performance

============================================================
44. AGENT ACTIVITY CENTER
=========================

Create:

/agent-activity

Show:

what agent is doing
current job
tools called
research found
strategy generated
backtest running
paper trade generated
ranking update

Example:

STRATEGY BUILDER

Generating:
"Indian Large Cap Breakout"

STATUS:
BACKTESTING

Agent chain:

ResearchAgent
->
StrategyBuilderAgent
->
BacktestAgent
->
CriticAgent

Do not expose hidden chain-of-thought.

Show only concise operational events, tool calls, decisions, and outputs.

============================================================
45. PREDICTION + STRATEGY SEPARATION
====================================

Prediction is NOT Strategy.

Prediction:

"Probability of 5D positive return = 72%."

Strategy:

"If probability > 70%, enter under these additional conditions..."

Allow strategies to combine:

prediction
technical
fundamental
F&O
market regime
risk

============================================================
46. PAPER PORTFOLIO
===================

Create paper portfolios:

Default portfolio:
₹10,00,000

Each strategy can have its own paper account.

Example:

Portfolio A:
Momentum

Portfolio B:
Value

Portfolio C:
AI Hybrid

Portfolio D:
Options

Portfolio E:
Agent Tournament

All isolated.

============================================================
47. PORTFOLIO ANALYTICS
=======================

Display:

capital
equity
cash
P&L
daily P&L
unrealized P&L
realized P&L
exposure
sector concentration
stock concentration
drawdown
beta
volatility

Later:

VaR
CVaR
stress testing

============================================================
48. RISK ENGINE
===============

Risk engine is deterministic.

Rules:

max_position
max_sector_exposure
max_portfolio_exposure
max_daily_loss
max_strategy_drawdown
max_volatility
max_leverage

Risk engine can:

block paper order
reduce simulated position
raise alert
mark strategy degraded

It must not silently override a strategy without recording the reason.

============================================================
49. NEWS / RESEARCH LAYER
=========================

Tavily is a research layer, not market-price infrastructure.

Use it for:

latest company developments
regulatory news
earnings commentary
management commentary
sector developments
macro context

Every research result:

source
url
published_at
retrieved_at
relevance
symbol mapping

Store research evidence.

============================================================
50. TELEGRAM
============

Telegram becomes remote dashboard.

User can ask:

"Market"

"HDFCBANK"

"Why is NIFTY falling?"

"Show today's signals"

"Show strategy rankings"

"Start paper trading Momentum v4"

"Pause Momentum v4"

"Why is Momentum v4 ranked #1?"

"Create a strategy for mean reversion"

The bot responds through Hermes.

Alert examples:

BULLISH SETUP
RISK ALERT
STRATEGY ALERT
PAPER TRADE
STRATEGY RANKING CHANGE
DAILY BRIEFING

============================================================
51. WHATSAPP
============

Implement provider abstraction.

Development can use Hermes-compatible WhatsApp integration.

Production should remain replaceable with official WhatsApp Business infrastructure.

Same command model as Telegram.

Do not tightly couple application code to a specific WhatsApp bridge.

============================================================
52. ALERT ENGINE
================

Create deterministic event rules.

Events:

PRICE_BREAKOUT
PRICE_BREAKDOWN
PREDICTION_CHANGE
RISK_CHANGE
NEWS_EVENT
FII_SHIFT
OI_SHIFT
STRATEGY_DEGRADATION
PAPER_LOSS_LIMIT
STRATEGY_RANK_CHANGE

Each event gets:

severity
timestamp
source
symbol
strategy_id if applicable
deduplication_key

============================================================
53. NOTIFICATION ROUTER
=======================

Route events:

dashboard
telegram
whatsapp

User preferences determine destination.

Do not send duplicate alerts.

Cooldowns:

configurable.

Example:

same risk trigger:
maximum one notification per 30 minutes

unless severity escalates.

============================================================
54. AVATAR
==========

Avatar is a presentation layer.

User uploads an image.

Use:

LivePortrait
MuseTalk
local TTS

The avatar can explain:

market briefing
prediction
strategy result
paper trade
strategy ranking
risk alert

Example:

Strategy result appears on dashboard.

Avatar:

"Momentum v4 remains number one because its out-of-sample performance is stronger than the other strategies, while maintaining lower drawdown."

The avatar must not invent metrics.

Numbers come from structured backend data.

============================================================
55. LOCAL TTS
=============

Default:

Kokoro

Optional:

Piper

Optional cloud:

Fish Audio

TTS abstraction:

speak()
stream()
voices()

The entire avatar system must work offline after model installation.

============================================================
56. OFFLINE MODE
================

Offline mode supports:

cached Indian market data
historical data
backtests
paper trading using cached/replayed data
strategy research using local datasets
Kokoro
avatar rendering
strategy ranking

It must clearly display:

OFFLINE

LAST MARKET DATA:
timestamp

Never imply live prices are available while offline.

============================================================
57. MARKET REPLAY MODE
======================

Create a powerful replay mode.

User chooses:

date
time
market

Example:

NIFTY:
15 March 2025
09:15 -> 15:30

System replays historical events chronologically.

The agent can experience the market as if it were live.

This is critical for testing strategies without future leakage.

============================================================
58. AGENT STRATEGY REPLAY
=========================

Allow the StrategyAgent to run against replayed historical sessions.

Agent receives only data available up to that timestamp.

It cannot access future outcomes.

After replay:

compare decisions to actual outcome.

This becomes an experimental environment.

============================================================
59. STRATEGY LEARNING DATASET
=============================

Store:

market_state
available_features
agent_hypothesis
strategy_rules
decision
trade
outcome
risk
reward

This forms a research dataset.

Do NOT immediately train the LLM on it.

First use it for:

strategy analysis
feature importance
failure analysis
calibration
agent evaluation

============================================================
60. AGENT EVALUATION
====================

Track agent performance separately from strategy performance.

Metrics:

hypotheses generated
strategies accepted
strategies rejected
backtest success
paper success
improvement rate
false positives
overfit rate
average strategy lifetime

Example:

StrategyBuilderAgent:

142 hypotheses
37 valid strategies
11 profitable out-of-sample
4 robust in paper
2 top-ranked

This tells us whether the agent is genuinely improving.

============================================================
61. SELF-IMPROVEMENT RULE
=========================

The agent may propose strategy changes.

It must NOT change the ranking formula.

It must NOT alter historical results.

It must NOT modify past trades.

It must NOT delete failed strategies.

It must NOT promote itself to live trading.

It must NOT redefine metrics after observing results.

Evaluation code is controlled infrastructure.

============================================================
62. REAL TRADING BOUNDARY
=========================

Do not build real trading in MVP.

Broker interfaces may exist as future adapters only.

If a live broker provider is added later:

paper
->
validated
->
user approval
->
compliance checks
->
explicit live mode

Never:

agent
->
automatic live order

without explicit user authorization and separate controls.

============================================================
63. FUTURE LIVE TRADING INTERFACE
=================================

Reserve an interface:

BrokerProvider:

get_account()
get_positions()
get_orders()
place_order()
cancel_order()

But for MVP:

place_order()
must be disabled or mocked.

============================================================
64. AI EXPLANATION CONTRACT
===========================

Any AI explanation must cite structured inputs internally.

Example:

{
"statement":
"Momentum v4 outperformed NIFTY by 8.3 percentage points.",

"evidence": [
{
"metric": "strategy_return",
"value": 0.214
},
{
"metric": "benchmark_return",
"value": 0.131
}
]
}

Hermes is not allowed to invent the value.

============================================================
65. DASHBOARD DESIGN
====================

Create these screens:

/

Overview

/india-market

/stocks

/stock/{symbol}

/indices

/sectors

/fno

/predictions

/signals

/strategies

/strategies/{id}

/strategy-lab

/strategy-ranking

/backtests

/paper-trading

/paper-portfolio/{id}

/portfolio

/risk

/research

/news

/agent-activity

/model-performance

/avatar-lab

/ai-tutor

/settings

============================================================
66. STOCK PAGE
==============

Each stock page:

header
price
change
volume
AI score
prediction
risk

chart

technical
fundamental
F&O
news
events
analyst-style explanation
historical predictions
strategy participation

Button:

ASK AI

Examples:

"Why is this bullish?"

"What invalidates the signal?"

"Which strategy likes this stock?"

"Show me the risk."

============================================================
67. STRATEGY PAGE
=================

Show:

Strategy name
Version
Status
Hypothesis
Rules
Universe
Capital
Backtest
Paper trading
Ranking

Tabs:

Overview
Rules
Backtest
Paper
Trades
Risk
Evolution
Agent Critique
Versions

============================================================
68. PAPER TRADING SCREEN
========================

Show:

virtual capital
equity
cash
P&L
drawdown
positions
open orders
recent trades

Buttons:

START
PAUSE
RESET

Require confirmation for reset.

============================================================
69. STRATEGY LAB SCREEN
=======================

Left:

strategy prompt

Middle:

formal strategy DSL

Right:

backtest preview

Bottom:

performance

Example:

USER INPUT:

"Find a robust Indian large-cap trend strategy."

AGENT OUTPUT:

Hypothesis
Rules
Risk
Expected failure conditions

Then:

[BACKTEST]

Then:

[DEPLOY TO PAPER]

============================================================
70. STRATEGY TOURNAMENT SCREEN
==============================

Top:

Tournament
Universe
Capital
Date range
Transaction costs

Leaderboard.

Live updates:

Rank changes
P&L
drawdown
trade count

Do not use animated visual effects that obscure numeric information.

============================================================
71. AGENT STRATEGY CREATION FLOW
================================

User:

"Build me a low-drawdown Indian momentum strategy."

Hermes Supervisor:

1. calls MarketAgent
2. calls QuantAgent
3. calls StrategyBuilderAgent
4. creates Strategy DSL
5. validates it
6. invokes BacktestAgent
7. invokes StrategyCriticAgent
8. proposes improvements
9. creates v2
10. backtests v2
11. compares v1 vs v2
12. optionally deploys selected version to paper account

The user sees the resulting chain of operational actions.

============================================================
72. STRATEGY AGENT SHOULD LEARN FROM FAILURES
=============================================

Example:

Strategy v5:
return +26%
max DD -28%
poor

Critic:
"Performance is driven by two short periods."

Strategy v6:
same signal
plus volatility filter

Backtest:
return +20%
max DD -13%

Critic:
"Improvement appears robust."

Paper:
+8% after 30 days

Ranking:
#2

The agent can then propose v7.

============================================================
73. STRATEGY RANKING RESEARCH
=============================

Create daily research job:

For every strategy:

update metrics

detect degradation

compare benchmark

compare peers

generate critique

identify candidate mutations

Do not modify live/paper strategy automatically unless configured as an experimental research strategy.

============================================================
74. EXPERIMENTAL STRATEGY SANDBOX
=================================

Create a special:

RESEARCH SANDBOX

Agents can:

generate strategies
run experiments
mutate parameters
run backtests
run historical replay

Nothing outside the sandbox changes.

This is the main area where autonomous agent behavior is allowed.

============================================================
75. STRATEGY PROMOTION
======================

Require:

backtest pass
out-of-sample pass
paper-trading pass
risk pass
stability pass

Then:

PROMOTION CANDIDATE

User explicitly approves any future transition beyond paper trading.

============================================================
76. SYSTEM SAFETY
=================

The following are forbidden to agents:

delete prediction history
delete paper trades
modify historical market data
modify benchmark values
modify ranking formulas
change performance metrics
alter backtest dates after seeing result
access future replay data
place real trades

All forbidden operations must fail closed.

============================================================
77. MODEL REGISTRY
==================

Create:

models

Fields:

model_id
model_type
version
training_dataset
feature_version
trained_at
validation_metrics
status

Statuses:

development
validation
production
retired

============================================================
78. STRATEGY REGISTRY
=====================

Every strategy has:

strategy_id
parent_id
version
created_by
agent
created_at
hypothesis
DSL
dataset
backtest_id
paper_account
ranking_score
status

This allows complete strategy lineage.

============================================================
79. EXPERIMENT REGISTRY
=======================

Every experiment:

experiment_id
hypothesis
strategy_versions
dataset
market_period
parameters
results
winner
loser
decision
agent_run_id

This becomes the scientific notebook of the AI system.

============================================================
80. AGENT MEMORY
================

Hermes memory can be used for:

user preferences
project context
workflow state

But financial truth should live in structured databases.

Do not use free-form agent memory as the canonical source of:

price
P&L
prediction
strategy score
trade history

============================================================
81. MCP DESIGN
==============

market-mcp:
quotes
candles
indices
breadth
sectors
FII/DII

prediction-mcp:
prediction
prediction_history
model_metrics

strategy-mcp:
create_strategy
validate_strategy
clone_strategy
mutate_strategy
rank_strategies

backtest-mcp:
create_backtest
run_backtest
get_results
compare

papertrade-mcp:
create_account
deploy_strategy
pause_strategy
get_positions
get_orders
get_pnl
reset_account

risk-mcp:
get_risk
calculate_exposure
stress_test

research-mcp:
search
company_research
news

alert-mcp:
create_rule
delete_rule
list_alerts
trigger_alert

avatar-mcp:
create_avatar
speak
stop
set_emotion
set_motion

============================================================
82. MCP CONCURRENCY
===================

Only enable parallel MCP execution for read-only operations that are safe concurrently.

Examples:

get_quote
get_fii_dii
get_market_breadth
get_news

may run in parallel.

Do not blindly parallelize:

create_strategy
mutate_strategy
paper order
portfolio update
database writes

Review race conditions.

============================================================
83. REAL-TIME EVENT SYSTEM
==========================

Use Redis Streams initially.

Events:

quote.updated
candle.closed
prediction.created
prediction.changed
signal.created
risk.changed
strategy.trade
strategy.rank_changed
strategy.degraded
news.important
alert.triggered

Subscribers:

dashboard
alert-engine
paper-trading
analytics
hermes-notifier

============================================================
84. REAL-TIME DASHBOARD
=======================

Use WebSockets.

Do not poll every component aggressively.

Stream:

price changes
prediction changes
signal changes
paper P&L
strategy ranking

The dashboard should update without refresh.

============================================================
85. NOTIFICATIONS
=================

Telegram:
primary first messaging channel.

WhatsApp:
second channel.

Every notification carries:

timestamp
symbol
event
severity
model/strategy version
summary

Example:

STRATEGY RANK CHANGE

Momentum v4:
#4 -> #2

Reason:
out-of-sample score improved
paper Sharpe improved

============================================================
86. AVATAR NOTIFICATION MODE
============================

When a major event is triggered:

Hermes may send response to avatar:

{
text,
emotion,
movement
}

Avatar says:

"Momentum v4 just moved into second place..."

Only use metrics returned by backend.

============================================================
87. AI TUTOR
============

The user can ask:

"Explain Sharpe."

"Why did this strategy lose?"

"Why does max drawdown matter?"

"Explain this option chain."

"Teach me FII/DII."

"Explain why the strategy is ranked #1."

The TeacherAgent must use actual structured platform data when answering platform-specific questions.

============================================================
88. FUTURISTIC AGENT HUD
========================

Create an optional small panel:

AGENT STATUS

MARKET AGENT
● LIVE

QUANT AGENT
● LIVE

RESEARCH
● SEARCHING

STRATEGY LAB
● BACKTESTING

PAPER TRADING
● LIVE

RISK
● MONITORING

Do not show private chain-of-thought.

Show concise operational status only.

============================================================
89. PERFORMANCE MONITORING
==========================

Track:

data latency
model latency
backtest latency
paper trade latency
alert latency
Hermes latency
TTS latency
avatar FPS
WebSocket latency
notification success

============================================================
90. API SECURITY
================

API credentials must exist only server side.

Environment variables/secrets manager.

Never expose:

broker keys
market API keys
Tavily key
Telegram token
WhatsApp token
Fish key

to browser.

============================================================
91. USER AUTHENTICATION
=======================

Create users.

Every resource belongs to a user:

avatar
watchlist
alerts
paper portfolios
strategies
strategies created by user
private research

Public benchmark data can be shared internally.

Private data must be isolated.

============================================================
92. PAPER TRADING RESET
=======================

Reset must create a new paper-account generation.

Never delete old history.

Account:

PAPER-001-GEN-1

After reset:

PAPER-001-GEN-2

Keep prior results.

============================================================
93. DATA REPRODUCIBILITY
========================

Every backtest must store:

dataset version
strategy version
feature version
execution model version
cost model version

Therefore if strategy v7 is rerun one year later, the system can explain why numbers differ.

============================================================
94. FINAL PRODUCT PRINCIPLE
===========================

The system is NOT:

"ChatGPT that predicts stocks."

It is:

INDIAN MARKET DATA
+
QUANTITATIVE MODELS
+
STRATEGY RESEARCH
+
BACKTESTING
+
PAPER TRADING
+
RANKING
+
AGENT ORCHESTRATION
+
ALERTS
+
EXPLANATION
+
AVATAR

Hermes is the agent operating layer.

The database and quantitative engines remain the source of truth.

============================================================
95. BUILD SEQUENCE
==================

BUILD IN THIS EXACT ORDER:

PHASE 1:
Repository + infrastructure

PHASE 2:
Indian market calendar

PHASE 3:
Indian market data abstraction

PHASE 4:
NIFTY/SENSEX/BANK NIFTY dashboard

PHASE 5:
Stock universe + stock pages

PHASE 6:
Feature engine

PHASE 7:
Market regime

PHASE 8:
Prediction engine

PHASE 9:
F&O dashboard

PHASE 10:
Backtesting

PHASE 11:
Strategy DSL

PHASE 12:
Strategy Lab

PHASE 13:
Paper trading

PHASE 14:
Strategy ranking

PHASE 15:
Strategy evolution

PHASE 16:
Hermes MCP integration

PHASE 17:
Tavily research

PHASE 18:
Alert engine

PHASE 19:
Telegram

PHASE 20:
WhatsApp

PHASE 21:
Portfolio/Risk

PHASE 22:
Local TTS

PHASE 23:
Image avatar

PHASE 24:
AI Tutor

PHASE 25:
Agent activity center

PHASE 26:
Production hardening

Do not skip phases.

============================================================
96. FIRST IDE TASK
==================

Implement PHASE 1 through PHASE 4 ONLY.

Deliver:

1. Monorepo
2. Docker development setup
3. PostgreSQL
4. Redis
5. FastAPI
6. Next.js
7. Shared types
8. MarketDataProvider interface
9. Trading calendar
10. Indian index schema
11. NIFTY dashboard
12. SENSEX dashboard
13. BANK NIFTY dashboard
14. India VIX
15. market status
16. live event infrastructure

Do not implement Hermes yet.

Do not implement avatar yet.

Do not implement live trading.

Do not implement strategy evolution yet.

============================================================
97. SECOND IDE TASK
===================

Implement:

feature engine
market regime
prediction engine
prediction registry

Deliver working prediction records.

============================================================
98. THIRD IDE TASK
==================

Implement:

Strategy DSL
Strategy Builder
Backtest Engine
Strategy Registry

Deliver:

one human-created strategy
one agent-created strategy
backtest comparison

============================================================
99. FOURTH IDE TASK
===================

Implement:

Paper Trading Engine
Dummy capital
Simulated execution
Paper P&L
Strategy deployment
Strategy leaderboard

Acceptance:

Two strategies run on the same ₹10,00,000 virtual account conditions and are ranked.

============================================================
100. FIFTH IDE TASK
===================

Implement:

StrategyEvolutionAgent.

Acceptance:

Agent creates strategy v1.

Backtests v1.

Critiques v1.

Creates v2.

Backtests v2.

Compares v1/v2.

Deploys selected version to paper.

Does NOT modify v1.

============================================================
101. SIXTH IDE TASK
===================

Add Hermes.

Hermes becomes supervisor.

Create MCP integrations.

Test:

"Analyse Indian market."

"Create a strategy."

"Backtest this strategy."

"Start paper trading it."

"Why did it lose?"

"Compare it with Momentum v3."

============================================================
102. SEVENTH IDE TASK
=====================

Add alerts.

Test:

prediction degradation

risk threshold

strategy drawdown

strategy rank change

paper trade event

============================================================
103. EIGHTH IDE TASK
====================

Add Telegram.

Acceptance:

market alert
strategy alert
paper-trading alert
daily briefing

============================================================
104. NINTH IDE TASK
===================

Add WhatsApp abstraction and connector.

============================================================
105. TENTH IDE TASK
===================

Add avatar + local Kokoro TTS.

============================================================
106. TEST COMMANDS
==================

Every phase must provide commands:

npm test / frontend tests
pytest
integration tests
e2e tests

Also:

docker compose up
docker compose down

Create:

make test
make dev
make backtest
make paper
make agent
make migrate

============================================================
107. ACCEPTANCE TEST — STRATEGY AUTONOMY
========================================

Run this complete scenario:

User:

"Find me a robust Indian large-cap momentum strategy with controlled drawdown."

System:

ResearchAgent
->
MarketAgent
->
StrategyBuilderAgent
->
Strategy DSL
->
validation
->
Backtest
->
CriticAgent
->
Mutation
->
Backtest
->
comparison
->
paper deployment

Then simulate market progression.

The system must:

record paper trades
calculate P&L
calculate drawdown
update strategy score
compare benchmark
update leaderboard

Finally Hermes reports:

Strategy:
Momentum v2

Backtest:
...

Paper:
...

Ranking:
#2

Reason:
...

Known weaknesses:
...

The strategy must remain fully reproducible from its stored version and dataset.

============================================================
108. ABSOLUTE RULES
===================

NO:
future leakage
look-ahead bias
fake market data
fabricated P&L
fabricated trade executions
fabricated performance
LLM-generated numerical facts without backend evidence
automatic real-money trading
uncontrolled self-modification
deletion of failed strategy history
silent modification of benchmarks
silent modification of scoring rules

YES:
versioning
auditability
paper trading
backtesting
out-of-sample validation
strategy tournaments
strategy lineage
agent experimentation
deterministic risk rules
structured evidence
explicit user approval for future live trading

============================================================
109. DEFINITION OF DONE
=======================

The MVP is successful when:

1. Indian market data is visible.
2. NIFTY/SENSEX/BANK NIFTY are working.
3. Stocks can be analyzed.
4. Predictions are recorded.
5. Strategies can be created.
6. Strategies can be backtested.
7. Strategies can trade virtual money.
8. Multiple strategies can compete.
9. Strategies receive objective rankings.
10. Agents can propose new strategies.
11. Agents can critique failed strategies.
12. Agents can create improved versions.
13. Strategy versions remain immutable.
14. Paper trading confirms or rejects backtests.
15. Hermes orchestrates the research workflow.
16. Telegram receives alerts.
17. WhatsApp is supported through an adapter.
18. The avatar can speak from an uploaded image.
19. TTS can operate locally.
20. Dashboard shows everything in real time.
21. No real-money trades can happen accidentally.
22. Every result can be traced back to data, model and strategy versions.

addtionn we can do 

I want to build a financial trading framework in Python that uses a team of specialized AI agents working together, kind of like a small trading firm. The whole thing should run from the command line.

The system should have a team of analyst agents: a fundamentals analyst looking at company financials, a sentiment analyst tracking social media mood, and a technical analyst for chart patterns. It also needs a news analyst for macroeconomic events.

After the analysts generate their reports, I want a researcher team where a "bullish" agent and a "bearish" agent debate the findings. A main "trader" agent will then use this information to decide on a trade. Finally, a risk management agent should review the plan before a portfolio manager agent gives the final approval.

It should support different LLMs, so make it easy for me to plug in my API keys for OpenAI, Gemini, Claude, and others in a `.env` file. Also, let's include Docker support to make setup easier.
