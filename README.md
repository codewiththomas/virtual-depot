# Virtual Depot

A virtual depot where assets (stocks/etf) can be managed. Uses Flask to run as webapp in browser. 

## Milestones

1. Have a virtual depot
   1. [ ] Manage cash balance
   2. [ ] Add Asset to depot (buy)
   3. [ ] Remove Asset from depot (sell)
   4. [x] Get historical data for assets in depot
   5. [ ] Calculate Value of depot
2. Enrich data
3. Develop trading strategies
4. Self-Trading

## Tech Stack

- Python 3.12
  - yfinance
  - sqlalchemy
  - flask
  - mkdocs
- SQLite 

## Quick Start

Clone repo.

```bash
git clone https://github.com/codewiththomas/trade-bot.git
```

Create a virtual environment.

```bash
py -3.12 -m venv .venv
```

Activate virtual environment.

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Navigate to `/src` folder.

```bash
cd src
```

Run the app.

```bash
python main.py
```
