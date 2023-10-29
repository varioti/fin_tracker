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
def crypto():
    if not 'logged_in' in session:
            return authenticate()
    return render_template("crypto/crypto.html", coins = Coin.query.all())