# Strategy: {{STRATEGY_NAME}}

## Hypothesis
{{One-sentence strategy thesis}}

## Strategy Type
{{strategy_type}}
<!-- One of: trend-following, mean-reversion, breakout, custom -->
<!-- Drives default success criteria values -->

## Asset & Timeframe
- **Asset:** {{asset}}
- **Exchange/Source:** {{data source}}
- **Timeframe:** {{timeframe}}
- **Date Range:** {{start}} to {{end}}

## Scope
{{Selected scope items from /brrr:new-milestone}}

- [ ] Strategy logic (entry/exit rules)
- [ ] Backtesting & optimization
- [ ] Parameter tuning
- [ ] Risk management
- [ ] PineScript export
- [ ] MD instructions export

## Success Criteria
- **Primary:** Sharpe Ratio > {{target}}
- **Secondary:** Max Drawdown < {{target}}%, Win Rate > {{target}}%
- **Minimum trades:** {{N}}

## Original Idea
{{User's original description, preserved as anchor for drift detection}}

---
*Created: {{date}}*
*Milestone: {{milestone_name}}*
