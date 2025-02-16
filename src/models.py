from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Beispiel: Asset-Typen
ASSET_TYPE_STOCK = "stock"
ASSET_TYPE_ETF = "etf"

class Asset(db.Model):
    """
    Tabelle für alle verfügbaren Assets (Aktien, ETFs, etc.).
    Enthält Meta-Informationen, z.B. Name, Symbol, Typ.
    """
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False, default=ASSET_TYPE_STOCK)

    # Optional: Historische Kursdaten (1:n) -> PriceHistory
    price_history = db.relationship("PriceHistory", backref="asset", lazy=True)

    def __repr__(self):
        return f"<Asset {self.symbol}>"

class PriceHistory(db.Model):
    """
    Speichert historische (Tages-)Schlusskurse für ein Asset.
    """
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PriceHistory {self.asset_id} {self.date} {self.close_price}>"

class Depot(db.Model):
    """
    Tabelle für das Depot selbst: beinhaltet Guthaben + Verweis auf Holdings.
    Hier könnte man auch mehrere User verwalten; Demo: nur 1 Depot.
    """
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)

    holdings = db.relationship("Holding", backref="depot", lazy=True)

    def __repr__(self):
        return f"<Depot {self.id} | Balance: {self.balance}>"

class Holding(db.Model):
    """
    Verknüpfungstabelle Depot <-> Asset mit Stückzahl, Kaufdatum, usw.
    """
    id = db.Column(db.Integer, primary_key=True)
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)

    quantity = db.Column(db.Float, nullable=False, default=0.0)  # Anzahl Aktien/ETF-Anteile
    average_cost = db.Column(db.Float, nullable=False, default=0.0)  # Durchschnittlicher Kaufpreis
    total_fees = db.Column(db.Float, nullable=False, default=0.0)    # Summe aller Gebühren

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Holding Depot:{self.depot_id}, Asset:{self.asset_id}, Qty:{self.quantity}>"

class Transaction(db.Model):
    """
    Speichert jede Transaktion (Kauf/Verkauf) mit Datum, Menge, Preis, Gebühr.
    """
    id = db.Column(db.Integer, primary_key=True)
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)

    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy' oder 'sell'
    quantity = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)  # Kauf-/Verkaufspreis
    fee = db.Column(db.Float, nullable=False, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.quantity}x Asset:{self.asset_id}>"
