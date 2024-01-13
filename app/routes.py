from app import app
from app.models import Coin, CryptoTransactions, CryptoManualPortfolio, CryptoPortfolioTimestamps
from config import SECRET_KEY
from flask import render_template, redirect, session, request, url_for

from app.utils.crypto_methods import deposit_totals, deposit_evolution, earn_evolution
from app.utils.api_methods import get_global_balance, get_price, get_orders
import pandas as pd
import json
import plotly
import plotly.express as px
from datetime import datetime

########
# AUTH #
########

def check_auth(p):
    return p == SECRET_KEY

def authenticate():
    return redirect('/crypto/login/')

@app.route('/crypto/login/', methods=['GET', 'POST'])
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

@app.route('/crypto/logout/')
def logout():
    session.pop('logged_in', None)
    return redirect('/crypto/login/')

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
    if not 'logged_in' in session:
        return authenticate()

    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404

    o = get_orders(coin.coin, "USD") + get_orders(coin.coin, "EUR")
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
    if not 'logged_in' in session:
        return authenticate()

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
    if not 'logged_in' in session:
        return authenticate()

    coin = Coin.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("list_coins"))

# Update a coin
@app.route("/crypto/coin/update/<int:id>", methods=["GET", "POST"])
def update_coin(id):
    if not 'logged_in' in session:
        return authenticate()

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
    if not 'logged_in' in session:
        return authenticate()

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
    if not 'logged_in' in session:
        return authenticate()

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

#############
# PORTFOLIO #
#############

@app.route("/crypto/portfolio/", methods=["GET","POST"])
def portfolio():
    if not 'logged_in' in session:
        return authenticate()

    # Get all the coins retrieved from the database
    manual_coins = CryptoManualPortfolio.query.all()
    manual_total = float(sum([coin.getUSDValue() for coin in manual_coins]))

    # Get all the coins retrieved from the APIs
    auto_total, auto_coins = get_global_balance()

    return render_template("portfolio/portfolio.html", coins = auto_coins, total_balance = auto_total + manual_total, manual_coins = manual_coins)

@app.route("/crypto/portfolio/add/", methods=["GET","POST"])
def portfolio_add():
    if not 'logged_in' in session:
        return authenticate()

    if request.method == "POST":
        # Get form data
        coin = request.form.get("asset")
        if get_price(coin) == 0:
            return "Coin not found", 404

        amount = request.form.get("amount")
        platform = request.form.get("platform")

        # Create a new coin record
        coin = CryptoManualPortfolio.create(
            asset=coin,
            amount=amount,
            platform=platform,
        )

        return redirect(url_for("portfolio"))

    return render_template("portfolio/add_coin.html")

@app.route("/crypto/portfolio/delete/<int:id>", methods=["GET", "POST"])
def portfolio_delete(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoManualPortfolio.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("portfolio"))

@app.route("/crypto/portfolio/update/<int:id>", methods=["GET", "POST"])
def portfolio_update(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoManualPortfolio.get(id)
    if coin is None:
        return "Coin not found", 404

    if request.method == "POST":
        # Get form data
        asset = request.form.get("asset")
        amount = request.form.get("amount")
        platform = request.form.get("platform")

        # Update the coin record
        coin.update(
            asset=asset,
            amount=amount,
            platform=platform,
        )

        return redirect(url_for("portfolio"))

    return render_template("portfolio/update_coin.html", asset=coin.asset, amount=coin.amount, platform=coin.platform)

#############
# Evolution #
#############

@app.route("/crypto/evolution/", methods=["GET","POST"])
def crypto_deposit():
        if not 'logged_in' in session:
            return authenticate()

        # Get deposit and portfolio timestamps historic sorted by date
        deposit_historic = CryptoTransactions.query.all()
        deposit_historic = sorted(deposit_historic, key=lambda x: x.deposit_date, reverse=True)

        portfolio_historic = CryptoPortfolioTimestamps.query.all()
        portfolio_historic = sorted(portfolio_historic, key=lambda x: x.pf_date, reverse=True)

        # Get coins in manual portfolio
        manual_coins = CryptoManualPortfolio.query.all()

        # SUMMARY
        totals_3 = deposit_totals(deposit_historic)
        evolution = deposit_evolution(deposit_historic)
        total_balance, balance = get_global_balance(manual_data=manual_coins)

        price_today = get_price("EUR")
        pf_today_eur = total_balance/price_today

        totals =(totals_3[0],totals_3[1],totals_3[2],pf_today_eur,pf_today_eur+totals_3[2])

        now_value_present = False
        now_timestamp = CryptoPortfolioTimestamps(pf_date=datetime.today().date(), amount=total_balance/price_today)
        if now_value_present:
            portfolio_historic[0] = now_timestamp
        else:
            portfolio_historic.insert(0,now_timestamp)
        now_timestamp=True

        earning = earn_evolution(evolution, portfolio_historic)

        print(len(earning[0]),len(earning[1]),len(earning[2]))
        print(len(evolution[0]),len(evolution[1]))

        # GRAPHIC OF EVOLUTION
        df2 = pd.DataFrame({
            "BDates": evolution[0],
            "Balance": evolution[1],
        })

        df = pd.DataFrame({
            "Dates": earning[0],
            "Portfolio": earning[1],
            "Profit": earning[2]
        })

        fig = px.line(df, x="Dates", y=["Portfolio","Profit"])
        fig.add_scatter(x=df2["BDates"], y=df2["Balance"], mode='lines')
        fig.data[2].name="Balance"
        fig.update_traces(showlegend=True)

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        header="Evolution"
        description = """Amount deposited and withdrawn"""

        # WEBPAGE
        return render_template("evolution/evolution.html", total_balance=total_balance, balance=balance, histo = deposit_historic, portfolio = portfolio_historic, totals = totals, graphJSON=graphJSON, header=header,description=description)

@app.route("/crypto/evolution/deposit/add/", methods=["GET","POST"])
def crypto_deposit_add():
    if not 'logged_in' in session:
        return authenticate()

    if request.method == "POST":
        # Get form data
        amount = request.form.get("amount")
        date = request.form.get("date")
        exchange = request.form.get("exchange")

        # Create a new coin record
        coin = CryptoTransactions.create(
            amount=amount,
            deposit_date=date,
            exchange=exchange,
        )

        return redirect(url_for("crypto_deposit"))

    return render_template("evolution/deposit_add.html")

@app.route("/crypto/evolution/deposit/delete/<int:id>", methods=["GET", "POST"])
def crypto_deposit_delete(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoTransactions.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("crypto_deposit"))

@app.route("/crypto/evolution/deposit/update/<int:id>", methods=["GET", "POST"])
def crypto_deposit_update(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoTransactions.get(id)
    if coin is None:
        return "Coin not found", 404

    if request.method == "POST":
        # Get form data
        amount = request.form.get("amount")
        date = request.form.get("date")
        platform = request.form.get("platform")

        # Update the coin record
        coin.update(
            amount=amount,
            deposit_date=date,
            exchange=platform,
        )

        return redirect(url_for("crypto_deposit"))

    return render_template("evolution/deposit_update.html", amount=coin.amount, date=coin.deposit_date, platform=coin.exchange)

@app.route("/crypto/evolution/timestamp/add/", methods=["GET","POST"])
def crypto_timestamp_add():
    if not 'logged_in' in session:
        return authenticate()

    if request.method == "POST":
        # Get form data
        amount = request.form.get("amount")
        date = request.form.get("date")

        # Create a new coin record
        coin = CryptoPortfolioTimestamps.create(
            amount=amount,
            pf_date=date,
        )

        return redirect(url_for("crypto_deposit"))

    today = datetime.today().date()
    return render_template("evolution/timestamp_add.html", today = today)

@app.route("/crypto/evolution/timestamp/delete/<int:id>", methods=["GET", "POST"])
def crypto_timestamp_delete(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoPortfolioTimestamps.get(id)
    if coin is None:
        return "Coin not found", 404

    # Delete the coin record
    coin.delete()

    return redirect(url_for("crypto_deposit"))

@app.route("/crypto/evolution/timestamp/update/<int:id>", methods=["GET", "POST"])
def crypto_timestamp_update(id):
    if not 'logged_in' in session:
        return authenticate()

    coin = CryptoPortfolioTimestamps.get(id)
    if coin is None:
        return "Coin not found", 404

    if request.method == "POST":
        # Get form data
        amount = request.form.get("amount")
        date = request.form.get("date")

        # Update the coin record
        coin.update(
            amount=amount,
            pf_date=date,
        )

        return redirect(url_for("crypto_deposit"))

    return render_template("evolution/timestamp_update.html", amount=coin.amount, date=coin.pf_date)
