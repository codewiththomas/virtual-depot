from app import app
from models import db, Asset
from data_service import fetch_and_store_price_history

def daily_update():
    with app.app_context():
        # Alle Assets, die im Depot liegen (oder allgemein existieren), aktualisieren
        assets = Asset.query.all()
        for asset in assets:
            print(f"Aktualisiere {asset.symbol} ...")
            fetch_and_store_price_history(asset.symbol)
        print("Tägliches Update abgeschlossen.")

if __name__ == "__main__":
    daily_update()
