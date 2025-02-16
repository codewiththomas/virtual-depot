import yfinance as yf
from datetime import datetime, timedelta
from models import db, Asset, PriceHistory

def fetch_and_store_price_history(asset_symbol: str):
    """
    Ruft historische Kursdaten (z.B. bis heute) von Yahoo Finance ab
    und speichert neue Einträge in der DB.
    """
    asset = Asset.query.filter_by(symbol=asset_symbol).first()
    if not asset:
        # Asset existiert nicht, wir legen es an. In Wirklichkeit
        # würdest du vorher die Asset-Infos (Name, Typ) definieren.
        asset = Asset(symbol=asset_symbol, name=asset_symbol, asset_type="stock")
        db.session.add(asset)
        db.session.commit()

    # Letztes gespeichertes Datum herausfinden
    last_entry = PriceHistory.query.filter_by(asset_id=asset.id).order_by(PriceHistory.date.desc()).first()
    if last_entry:
        start_date = last_entry.date + timedelta(days=1)
    else:
        # Falls keine Daten vorhanden sind, hol z.B. die letzten 2 Jahre
        start_date = datetime.now() - timedelta(days=730)

    end_date = datetime.now()

    # Hol Daten mit yfinance
    # interval='1d' = Tagesdaten
    data = yf.download(asset_symbol, start=start_date, end=end_date, interval='1d', progress=False)

    # DataFrame verarbeiten
    for index, row in data.iterrows():
        date = index.date()
        close_price = float(row['Close'])

        # In DB speichern, wenn noch nicht vorhanden
        # (zur Sicherheit könnte man auch checken, ob das Datum schon existiert)
        ph = PriceHistory(asset_id=asset.id, date=date, close_price=close_price)
        db.session.add(ph)

    db.session.commit()
    return True
