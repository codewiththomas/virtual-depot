# Virtual Depot

A virtual depot where assets (stocks/etf) can be managed. Uses Flask to run as webapp in browser.

## Tech Stack

- Python 3.12
  - yfinance
  - sqlalchemy
  - flask
  - mkdocs
- SQLite

## Milestones

1. Have a virtual depot
   1. [x] Manage cash balance
   2. [x] Add Asset to depot (buy)
   3. [x] Remove Asset from depot (sell)
   4. [x] Get historical data for assets in depot
   5. [x] Calculate Value of depot
2. Enrich data
   1. Calculate KPIs for assets
      1. [x] SMA (Simple Moving Average)
      2. [x] RSI (Relative Strength Index)
      3. [x] Bollinger Bands
      4. [ ] MACD (Moving Average Convergence Divergence)
      5. [ ] OBV (On Balance Volume)
      6. [ ] ATR (Average True Range)
      7. [ ] ADX (Average Directional Index)
      8. [ ] Stochastic Oscillator
      9. [ ] Momentum
      10. [ ] Volatility
      11. [ ] Beta
      12. [ ] Sharpe Ratio
      13. [ ] Sortino Ratio
      14. [ ] Treynor Ratio
      15. [ ] Information Ratio
      16. [ ] Jensen's Alpha
      17. [ ] Tracking Error
      18. [ ] Maximum Drawdown
      19. [ ] Calmar Ratio
      20. [ ] Pain Index
      21. [ ] Ulcer Index
      22. [ ] Value at Risk
      23. [ ] Conditional Value at Risk
      24. [ ] Expected Shortfall
      25. [ ] Tail Ratio
      26. [ ] Skewness
      27. [ ] Kurtosis
      28. [ ] Max Loss
   1. Enrich with market data
3. Develop trading strategies
4. Self-Trading
