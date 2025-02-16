# Getting Started

## Start the application

Clone repo.

```bash
git clone https://github.com/codewiththomas/virtual-depot.git
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

## Code Structure

```bash
src/
├── app.py                   # Entry point for the Flask-App
├── config.py                # Configuration as database connection string
├── requirements.txt         # Dependency management
├── daily_update.py          # Script for daily update of financial data
├── data_service.py          # Service to pull financial data from Yahoo Finance API and write to database
├── indicators.py            # Various functions to calculate KPIs
├── models.py                # SQLAlchemy-Models
├── static/                  # Folder for static files (Bootstrap, CSS, JS)
├── templates/               # HTML-Templates
└── ...
```
