# Trading Bot

The goal is to create a trading bot that can be used to trade on the stock market. The bot should be able to trade on
different stock exchanges and with different assets. The bot should be able to trade with different strategies and
should be able to learn from the past.

## Basic Idea

Goal:

- Check depot once a day and decide if trades should be made
- For 30 days period, the depot should not drop below 90%
- Target is to maximize the depot value

Setting up the bot

- the bot gets a virtual start balance
- the bot gets a virtual depot
- the bot gets a list of all tradeable assets
- the bot gets an imaginary date (allows us to test the bot in the past)
- give bot the info that each trade costs a certain amount of money (1 EUR)

Preparing data basis

- pull financial data from the Yahoo Finance API for each asset
- store the data in a SQLite database
- use incremental updates (first run, pull max period for each asset, then pull and save only the new data)

Enrich data basis

- calculate KPIs for each asset
  - SMA (Simple Moving Average) - short, medium, long
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - MACD (Moving Average Convergence Divergence)
  - OBV (On Balance Volume)

Trading

- decide if any assets should be sold in order to buy better ones

## Financial Data

The fincancial data are pulled from the Yahoo Finance API and stored in a SQLite database.

## Classes

- Asset - as single asset
- Depot - as depot of assets
- Bot - as trading bot

KPIs for single instruments:

- Short SMA (20 Tage)
- Long SMS (50 Tage)
- RSI (14-Tage)
- Bollinger Bands (n=20, up/down)
- MACD (Moving Average Convergence Divergence)
- OBV (On Balance Volume)
