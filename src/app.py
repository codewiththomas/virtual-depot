from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Depot, Asset, Holding, Transaction
from data_service import fetch_and_store_price_history
from indicators import calculate_sma, calculate_rsi, calculate_bollinger_bands

import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Beim ersten Start die DB erstellen (oder per Flask-Migrate)
with app.app_context():
    db.create_all()
    # Falls noch kein Depot existiert, legen wir eins an (Startbalance = 0).
    if not Depot.query.first():
        depot = Depot(balance=0.0)  # Startguthaben = 0
        db.session.add(depot)
        db.session.commit()

@app.route("/")
def index():
    """
    Zeigt eine Übersicht über das Depot:
      - Aktueller Kontostand
      - Liste der Holdings (Assets + Anzahl + aktueller Wert)
      - Gesamtwert
    """
    depot = Depot.query.first()
    if not depot:
        flash("Kein Depot vorhanden.")
        return redirect(url_for("search_asset"))

    holdings = depot.holdings
    total_value = 0.0

    holdings_info = []
    for holding in holdings:
        asset = Asset.query.get(holding.asset_id)
        last_price = 0.0
        if asset.price_history:
            last_price = asset.price_history[-1].close_price
        holding_value = holding.quantity * last_price
        total_value += holding_value

        holdings_info.append({
            "symbol": asset.symbol,
            "name": asset.name,
            "quantity": holding.quantity,
            "average_cost": holding.average_cost,
            "current_price": last_price,
            "holding_value": holding_value
        })

    return render_template("index.html",
                           depot=depot,
                           holdings=holdings_info,
                           total_value=total_value)

@app.route("/add_balance", methods=["POST"])
def add_balance():
    amount = float(request.form.get("amount", 0.0))
    depot = Depot.query.first()
    depot.balance += amount
    db.session.commit()
    flash(f"{amount:.2f} € wurden dem Depot hinzugefügt.")
    return redirect(url_for("index"))

@app.route("/search_asset", methods=["GET", "POST"])
def search_asset():
    if request.method == "POST":
        symbol = request.form.get("symbol").upper().strip()
        fetch_and_store_price_history(symbol)
        return redirect(url_for("view_asset", symbol=symbol))
    return render_template("search_asset.html")

@app.route("/asset/<symbol>")
def view_asset(symbol):
    asset = Asset.query.filter_by(symbol=symbol).first()
    if not asset:
        flash("Asset nicht gefunden.")
        return redirect(url_for("search_asset"))

    # Depot/Holding checken, ob Asset im Depot ist
    depot = Depot.query.first()
    holding = None
    for h in depot.holdings:
        if h.asset_id == asset.id:
            holding = h
            break

    history_entries = asset.price_history[-100:]  # letzte 100
    if not history_entries:
        flash("Keine Kursdaten verfügbar.")
        return redirect(url_for("search_asset"))

    # In DataFrame packen
    df = pd.DataFrame([{"date": h.date, "close": h.close_price} for h in history_entries])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    # Indikatoren
    df["SMA5"] = calculate_sma(df["close"], 5)
    df["SMA20"] = calculate_sma(df["close"], 20)
    df["RSI14"] = calculate_rsi(df["close"], 14)
    sma20, upper_b, lower_b = calculate_bollinger_bands(df["close"], 20)
    df["BB_MID"] = sma20
    df["BB_UPPER"] = upper_b
    df["BB_LOWER"] = lower_b

    latest_price = df["close"].iloc[-1]

    return render_template("view_asset.html",
                           asset=asset,
                           depot=depot,
                           holding=holding,
                           df=df.tail(30),
                           latest_price=latest_price)

@app.route("/buy_asset", methods=["POST"])
def buy_asset():
    symbol = request.form.get("symbol").upper().strip()
    quantity = float(request.form.get("quantity", 0))
    fee = float(request.form.get("fee", 0))

    depot = Depot.query.first()
    asset = Asset.query.filter_by(symbol=symbol).first()
    if not asset:
        flash("Asset nicht gefunden.")
        return redirect(url_for("search_asset"))

    if not asset.price_history:
        flash("Keine Kursdaten vorhanden. Bitte erst aktualisieren.")
        return redirect(url_for("view_asset", symbol=symbol))

    current_price = asset.price_history[-1].close_price
    total_cost = current_price * quantity + fee

    if depot.balance < total_cost:
        flash("Nicht genug Guthaben für diesen Kauf.")
        return redirect(url_for("view_asset", symbol=symbol))

    # Guthaben anpassen
    depot.balance -= total_cost

    # Holding updaten oder erstellen
    holding = None
    for h in depot.holdings:
        if h.asset_id == asset.id:
            holding = h
            break

    if holding:
        old_total_shares_cost = holding.average_cost * holding.quantity
        new_total_shares_cost = old_total_shares_cost + (current_price * quantity)
        new_quantity = holding.quantity + quantity
        holding.average_cost = new_total_shares_cost / new_quantity
        holding.quantity = new_quantity
        holding.total_fees += fee
    else:
        holding = Holding(
            depot_id=depot.id,
            asset_id=asset.id,
            quantity=quantity,
            average_cost=current_price,
            total_fees=fee
        )
        db.session.add(holding)

    # Transaction
    transaction = Transaction(
        depot_id=depot.id,
        asset_id=asset.id,
        transaction_type="buy",
        quantity=quantity,
        price_per_unit=current_price,
        fee=fee
    )
    db.session.add(transaction)
    db.session.commit()

    flash(f"{quantity:.2f} Stück(e) von {symbol} gekauft zum Preis von {current_price:.2f} pro Stück.")
    return redirect(url_for("index"))

@app.route("/sell_asset", methods=["POST"])
def sell_asset():
    symbol = request.form.get("symbol").upper().strip()
    quantity = float(request.form.get("quantity", 0))
    fee = float(request.form.get("fee", 0))

    depot = Depot.query.first()
    asset = Asset.query.filter_by(symbol=symbol).first()
    if not asset:
        flash("Asset nicht gefunden.")
        return redirect(url_for("search_asset"))

    if not asset.price_history:
        flash("Keine Kursdaten vorhanden.")
        return redirect(url_for("view_asset", symbol=symbol))

    current_price = asset.price_history[-1].close_price

    # Holding prüfen
    holding = None
    for h in depot.holdings:
        if h.asset_id == asset.id:
            holding = h
            break

    if not holding or holding.quantity < quantity:
        flash("Nicht genügend Stücke im Depot.")
        return redirect(url_for("view_asset", symbol=symbol))

    total_revenue = current_price * quantity - fee
    depot.balance += total_revenue

    holding.quantity -= quantity
    holding.total_fees += fee
    if holding.quantity == 0:
        db.session.delete(holding)

    transaction = Transaction(
        depot_id=depot.id,
        asset_id=asset.id,
        transaction_type="sell",
        quantity=quantity,
        price_per_unit=current_price,
        fee=fee
    )
    db.session.add(transaction)
    db.session.commit()

    flash(f"{quantity:.2f} Stück(e) von {symbol} verkauft zum Preis von {current_price:.2f} pro Stück.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
