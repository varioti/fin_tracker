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
    return render_template("coins/orders.html", coin=coin)

# Create a new coin
@app.route("/crypto/create_coin", methods=["GET", "POST"])
def create_coin():
    if request.method == "POST":
        # Get form data
        coin = request.form.get("coin")
        if get_price(coin) == 0:
            return "Coin not found", 404

        # Create a new coin record
        coin = Coin.create_coin(
            coin=coin,
            total_bought=0,
            mean_bought=0,
            total_sold=0,
            mean_sold=0,
            last_tr_total=0,
            last_tr_mean=0,
        )

        return redirect(url_for("list_coins"))

    return render_template("crypto/create_coin.html")

# Delete a coin
@app.route("/crypto/delete_coin/<int:id>", methods=["POST"])
def delete_coin(id):
    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("list_coins"))