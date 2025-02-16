import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from models import db, Asset, PriceHistory

def fetch_and_store_price_history(asset_symbol: str):
    """
    Ruft Kursdaten (Open, High, Low, Close, Volume) und
    Dividenden/Splits von Yahoo Finance ab und speichert
    sie in der DB. Inkrementell (nur neue Tage).
    """
    # Prüfen, ob Asset schon existiert
    asset = Asset.query.filter_by(symbol=asset_symbol).first()
    if not asset:
        # Asset noch nicht angelegt -> wir legen es an (mit einfachem Namen)
        asset = Asset(symbol=asset_symbol, name=asset_symbol, asset_type="stock")
        db.session.add(asset)
        db.session.commit()

    # Letztes gespeichertes Datum ermitteln
    last_entry = PriceHistory.query.filter_by(asset_id=asset.id).order_by(PriceHistory.date.desc()).first()

    if last_entry:
        # Starte ab dem nächsten Tag nach dem letzten gespeicherten Datum
        start_date = last_entry.date + timedelta(days=1)
        end_date = datetime.now().date()  # heute
        # Abruf
        data = yf.download(
            asset_symbol,
            start=start_date,
            end=end_date,
            interval='1d',
            actions=True,       # Hiermit kommen Dividends und Stock Splits
            progress=False,
            group_by='column'
        )
    else:
        # Noch keine Daten vorhanden -> komplette Historie
        data = yf.download(
            asset_symbol,
            period='max',
            interval='1d',
            actions=True,
            progress=False,
            group_by='column'
        )

    if data is None or data.empty:
        print(f"Keine Daten für {asset_symbol} erhalten.")
        return False

    # yfinance-DataFrame enthält nun Spalten:
    # ["Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividends", "Stock Splits"]
    #print(data)
    print("COLUMNS:", data.columns)

    if data.columns.nlevels > 1:
        data = data.xs(asset_symbol, level=1, axis=1)

    # Iterieren über alle Zeilen
    for index, row in data.iterrows():
        # index ist meist ein pandas.Timestamp
        date = index.date()

        # Check, ob es den Datensatz (date) schon gibt:
        exists = PriceHistory.query.filter_by(asset_id=asset.id, date=date).first()
        if exists:
            continue  # überspringen

        # Neue PriceHistory-Instanz
        ph = PriceHistory(
            asset_id=asset.id,
            date=date,
            open_price=float(row['Open']) if not pd.isna(row['Open']) else None,
            high_price=float(row['High']) if not pd.isna(row['High']) else None,
            low_price=float(row['Low']) if not pd.isna(row['Low']) else None,
            close_price=float(row['Close']) if not pd.isna(row['Close']) else None,
            volume=int(row['Volume']) if not pd.isna(row['Volume']) else 0,
            dividends=float(row['Dividends']) if 'Dividends' in row else 0.0,
            stock_splits=float(row['Stock Splits']) if 'Stock Splits' in row else 0.0
        )
        db.session.add(ph)

    db.session.commit()
    return True
