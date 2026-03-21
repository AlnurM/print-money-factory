# Milestone State

## Status
- **Milestone:** {{name}}
- **Status:** {{IN PROGRESS|APPROVED|ABANDONED}}
- **Current Phase:** {{N}}
- **Current Step:** {{discuss|research|plan|execute|verify}}
- **Created:** {{date}}
- **Last Updated:** {{date}}

## Scope
{{scope_items}}

- [ ] Strategy logic (entry/exit rules)
- [ ] Backtesting & optimization
- [ ] Parameter tuning
- [ ] Risk management
- [ ] PineScript export
- [ ] MD instructions export

## Data Source
- **Asset:** {{asset}}
- **Exchange/Source:** {{exchange_source}}
- **Timeframe:** {{timeframe}}
- **Date Range:** {{date_start}} to {{date_end}}

## Success Criteria
- **Primary:** Sharpe Ratio > {{sharpe_target}}
- **Max Drawdown:** < {{maxdd_target}}%
- **Minimum Trades:** {{min_trades}}
- **Type:** {{strategy_type}}

## Phases
### Phase {{N}}
- [ ] Discuss
- [ ] Research (optional)
- [ ] Plan
- [ ] Execute
- [ ] Verify

## Best Results
| Phase | Sharpe | Max DD | Trades | Verdict |
|-------|--------|--------|--------|---------|
{{rows}}

## Processed Context
| File | Processed | Description |
|------|-----------|-------------|
{{processed_context_rows}}

## History
<!-- Format: ### YYYY-MM-DD -- Event description -->
<!-- Newest entries first (append-only) -->
{{history_entries}}

---
*Milestone state tracker -- updated automatically by /brrr commands*
