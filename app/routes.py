from app import app, db
from app.models import *  
from config import SECRET_KEY
from flask import render_template, redirect, session, request, url_for

from app.utils.crypto_methods import deposit_totals, deposit_evolution, earn_evolution, get_track_balances
from app.utils.api_methods import get_global_balance, get_price, get_orders
import pandas as pd
import json
import plotly
import plotly.express as px
from datetime import datetime

########
# AUTH #
########

@app.route("/", methods=["GET","POST"])
def index():
    return redirect('/login/')


def check_auth(p):
    return p == SECRET_KEY

def authenticate():
    return redirect('/login/')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if check_auth(request.form['password']):
            session['logged_in'] = True
            return redirect('/crypto/')
    return '''
        <h1>Password needed to enter</h1>
        <form method="post">
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    return redirect('/login/')

##########
# CRYPTO #
##########

@app.route("/crypto/", methods=["GET","POST"])
def list_coins():
    if not 'logged_in' in session:
            return authenticate()
    return render_template("coins/crypto.html", coins = Coin.query.all())

# Read a coin (display details)
@app.route("/crypto/coin/<int:id>", methods=["GET"])
def read_coin(id):
    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404
    
    o = get_orders(coin.coin, "BUSD") + get_orders(coin.coin, "USDT") + get_orders(coin.coin, "EUR", False)
    # Sort the list of orders with descending date
    sorted_orders = sorted(o, key=lambda x: x['time'], reverse=True)

    # Convert timestamps into datetime
    for order in sorted_orders:
        time = datetime.fromtimestamp(int(order["time"])/1000).strftime('%Y-%m-%d %H:%M')
        order["time"] = time

    # Get the last transaction
    coin_last = [coin.last_tr_total, coin.last_tr_mean, coin.id]

    return render_template("coins/orders.html", coin = coin.coin, orders = sorted_orders, last_order = coin_last, coin_object=coin)

# Create a new coin
@app.route("/crypto/coin/create/", methods=["GET", "POST"])
def create_coin():
    if request.method == "POST":
        # Get form data
        coin = request.form.get("coin")
        if get_price(coin) == 0:
            return "Coin not found", 404

        # Create a new coin record
        coin = Coin.create(
            coin=coin,
            total_bought=0,
            mean_bought=0,
            total_sold=0,
            mean_sold=0,
            last_tr_total=0,
            last_tr_mean=0,
        )

        return redirect(url_for("list_coins"))

    return render_template("coins/create_coin.html")

# Delete a coin
@app.route("/crypto/coin/delete/<int:id>", methods=["POST"])
def delete_coin(id):
    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("list_coins"))

# Update a coin
@app.route("/crypto/coin/update/<int:id>", methods=["GET", "POST"])
def update_coin(id):
    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404

    if request.method == "POST":
        # Get form data
        total_bought = request.form.get("total_bought")
        mean_bought = request.form.get("mean_bought")
        total_sold = request.form.get("total_sold")
        mean_sold = request.form.get("mean_sold")
        last_tr_total = request.form.get("last_tr_total")
        last_tr_mean = request.form.get("last_tr_mean")

        # Update the coin record
        coin.update(
            total_bought=total_bought,
            mean_bought=mean_bought,
            total_sold=total_sold,
            mean_sold=mean_sold,
            last_tr_total=last_tr_total,
            last_tr_mean=last_tr_mean,
        )

        return redirect(url_for("list_coins"))

    return render_template("coins/update_coin.html", coin=coin)

# [TRANSACTION] Add a new buy transaction for this coin
@app.route("/crypto/coin/<int:id>/buy/", methods=["GET","POST"])
def add_buy_order(id):
        coin = Coin.get(id)
        if coin is None:
            return "Coin not found", 404

        # Show the add page (when clicked)
        if request.method == "GET":
                return render_template("coins/orders_add_buy.html", coin = coin.coin, id = id)

        # Otherwise (POST) : add the new task in the dict and show the home page
        _amount = request.form["amount"]
        _price = request.form["price"]
        if _amount and _price:
            coin.addBuyTransaction(float(_amount),float(_price))

        return redirect(url_for("read_coin", id=id))

# [TRANSACTION] Add a new buy transaction for this coin
@app.route("/crypto/coin/<int:id>/sell/", methods=["GET","POST"])
def add_sell_order(id):
        coin = Coin.get(id)
        if coin is None:
            return "Coin not found", 404

        # Show the add page (when clicked)
        if request.method == "GET":
                return render_template("coins/orders_add_sell.html", coin = coin.coin, id = id)

        # Otherwise (POST) : add the new task in the dict and show the home page
        _amount = request.form["amount"]
        _price = request.form["price"]
        if _amount and _price:
            coin.addSellTransaction(float(_amount),float(_price))

        return redirect(url_for("read_coin", id=id))