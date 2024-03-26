import hmac
import hashlib
import requests
import json
from json.decoder import JSONDecodeError
import time

from config import BINANCE_API_SECRET, BINANCE_API_KEY, ETHERSCAN_API_KEY, ETHERSCAN_ADDRESS, BTC_ADDRESS

uri = "https://api.binance.com"
binance_api_key = BINANCE_API_KEY
binance_api_secret = BINANCE_API_SECRET
etherscan_api_key = ETHERSCAN_API_KEY
etherscan_address = ETHERSCAN_ADDRESS
btc_address = BTC_ADDRESS

def get_timestamp_offset():
    url = "{}/api/v3/time".format(uri)

    payload = {}
    headers = {
      "Content-Type": "application/json"
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["serverTime"] - int(time.time() * 1000)

def generate_signature(query_string):
    m = hmac.new(binance_api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256)
    return m.hexdigest()

# Symbols
def get_symbols(coin, coin2=""):
    """ Get all Binance symbols (trading pairs) related to a coin

        Parameters:
        -----------
        - coin (str): symbol name of a coin (BTC, ETH, USDT, ...)
        - coin2 (str) [opt]: symbol name of a second coin (USD, ETH, USDT, ...)

        Returns:
        --------
        - symbols (list<str>): all symbols (trading pairs) related to these coins (BTCUSDT, ETHBTC, ...)
    """
    # Init query: gather all Binance symbols
    url = "{}/api/v3/exchangeInfo".format(uri)
    result = json.loads(requests.request("GET", url).text)

    # Filter result
    coin = coin.upper()
    symbols = [x["symbol"] for x in result["symbols"] if (coin in x["symbol"] and coin2 in x["symbol"])]

    return symbols

# ORDERS
def get_orders(coin, coin2=""):
    """ Get all Binance orders related to a coin

        Parameters:
        -----------
        - coin (str): symbol name of a coin (BTC, ETH, USDT, ...)
        - coin2 (str) [opt]: symbol name of a second coin (USD, ETH, USDT, ...)

        Returns:
        --------
        - orders (list<dict>): all orders related to these coins (see Binance API doc)
    """
    # Load all symbols available for coins provided
    symbols = get_symbols(coin, coin2)
    print(symbols)
    if len(symbols) == 0:
        return []

    # Loop over all symbols available
    orders = []
    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }
    for symbol in symbols:
        timestamp = int(time.time() * 1000 + get_timestamp_offset())
        query_string = "symbol={}&timestamp={}".format(symbol,timestamp)
        signature = generate_signature(query_string)
        url = "{}/api/v3/allOrders?{}&signature={}".format(uri, query_string, signature)
        symbol_orders = json.loads(requests.request("GET", url, headers=headers, data=payload).text)

        # Compute quantity in usd if it's not already the case
        if not "USD" in symbol :
            for i in range(len(symbol_orders)):
                # must compute usd price with second symbol
                if symbol.startswith(coin): # coin is 1st symbol
                    price = get_price(symbol.replace(coin, "", 1))
                else: # coin is 2nd symbol
                    price = get_price(coin)

                # Change to have USD qtt (and save origin value in a new field)
                original_qtt = symbol_orders[i]["cummulativeQuoteQty"]

                new_qtt = price * float(original_qtt)
                symbol_orders[i]["cummulativeQuoteQty"] = new_qtt
                symbol_orders[i]["originCummulativeQuoteQty"] = original_qtt

        orders = orders + symbol_orders

    return orders

# Price
def get_price(symbol1,symbol2="USD"):
    if symbol2 in symbol1:
        return 1

    url = "{}/api/v3/ticker/price".format(uri)

    all_prices = requests.get(url).json()
    for p in all_prices :
        try:
            s = p["symbol"]
            if symbol1.upper() in s and symbol2.upper() in s :
                for i in range(len(symbol1)) :
                    if symbol1[i].upper() == s[0] : # price in function of symbol 1
                        return float(p["price"])

                return 1/float(p["price"])
        except:
            print(p + " is a problem")
            return 0

def get_spot_balance():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/api/v3/account?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)["balances"]

def get_funding_balance():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "status=HOLDING&timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/asset/get-funding-asset?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    return json.loads(requests.request("POST", url, headers=headers, data=payload).text)

def get_earn_positions():
    """ Get all flexible and locked products positions from Binance API

        Returns:
        --------
        - positions (list<dict>): all felxible and locked positions related to these coins (see Binance API doc)
    """
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url_flex = "{}/sapi/v1/simple-earn/flexible/position?{}&signature={}".format(uri, query_string, signature)
    url_lock = "{}/sapi/v1/simple-earn/locked/position?{}&signature={}".format(uri, query_string, signature)
    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    flexible_positions = json.loads(requests.request("GET", url_flex, headers=headers, data=payload).text)["rows"]
    locked_positions = json.loads(requests.request("GET", url_lock, headers=headers, data=payload).text)["rows"]

    return flexible_positions + locked_positions

def get_blockchain_balance(address):
    # Check address
    if len(address) != 42:
        return 0, 0

    url = f"https://blockchain.info/balance?active={address}"

    response = requests.get(url)

    # Check if the response is empty or not in JSON format
    if not response.text:
        return 0, 0

    try:
        balance_in_sat = int(json.loads(response.text)[address]["final_balance"])
    except json.decoder.JSONDecodeError:
        return 0, 0

    balance_in_btc = balance_in_sat / 10**8

    price_usd = get_price("BTC", "USD")
    balance_in_usd = balance_in_btc * price_usd

    return balance_in_btc, balance_in_usd

def get_etherscan_balance(address="", etherscan_api_key=""):
    # Check address
    if len(address) != 42 or etherscan_api_key == "":
        return 0, 0

    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={etherscan_api_key}"
    response = requests.get(url)
    balance_in_wei = json.loads(response.text)["result"]

    balance_in_ether = int(balance_in_wei) / 10**18 # Convert Wei to Ether (1 Ether = 10^18 Wei)
    price_usd = get_price("ETH","USD")
    balance_in_usd = balance_in_ether * price_usd

    return balance_in_ether, balance_in_usd

def get_global_balance(manual_data=[], auto_data=[]):
    # INIT
    balance = 0
    assets = {}

    if len(auto_data) == 0:
        # SIMPLE EARN
        earn_positions = get_earn_positions()
        for pos in earn_positions :
            if "totalAmount" in pos and float(pos["totalAmount"]) > 0:
                amount = float(pos["totalAmount"])
                price_usd = get_price(pos["asset"],"USD")
                amount_usd = amount * price_usd
                balance = balance + amount_usd
                if not pos["asset"] in assets :
                    price_usd = get_price(pos["asset"],"USD")
                    assets[pos["asset"]] = {"asset":pos["asset"], "amount":amount, "usd":amount_usd, "platform":"BINANCE Earn"}
                else :
                    assets[pos["asset"]]["amount"] += amount
                    assets[pos["asset"]]["usd"] += amount_usd


        # FUNDINGS
        fundings = get_funding_balance()
        for f in fundings :
            if not (f["free"] is None) :
                price_usd = get_price(f["asset"],"USD")
                p = float(f["free"])*price_usd
                balance += p

                if not f["asset"] in assets :
                    assets[f["asset"]] = {"asset":f["asset"], "amount":float(f["free"]), "usd":p, "platform":"BINANCE Fundings"}
                else :
                    assets[f["asset"]]["amount"] += float(f["free"])
                    assets[f["asset"]]["usd"] += p
                    if "Fundings" not in assets[f["asset"]]["platform"] :
                        assets[f["asset"]]["platform"] += " & Fundings"

        # SPOT
        spots = get_spot_balance()
        for s in spots :
            if s["asset"][0:2] != "LD":
                if (not s["free"] is None) and float(s["free"]) > 0 :
                    price_usd = get_price(s["asset"],"USD")
                    if (price_usd is not None) :
                        p = float(s["free"])*price_usd
                        balance += p
                        if not s["asset"] in assets :
                            assets[s["asset"]] = {"asset":s["asset"], "amount":float(s["free"]), "usd":p, "platform":"BINANCE Spot"}
                        else :
                            assets[s["asset"]]["amount"] += float(s["free"])
                            assets[s["asset"]]["usd"] += p
                            if "Spot" not in assets[s["asset"]]["platform"] :
                                assets[s["asset"]]["platform"] += " & Spot"

                if (not s["locked"] is None) and float(s["locked"]) > 0:
                    price_usd = get_price(s["asset"],"USD")
                    if (price_usd is not None) :
                        p = float(s["free"])*price_usd
                        balance += p
                        if not s["asset"] in assets :
                            assets[s["asset"]] = {"asset":s["asset"], "amount":float(s["locked"]), "usd":p, "platform":"BINANCE Spot"}
                        else :
                            assets[s["asset"]]["amount"] += float(s["locked"])
                            assets[s["asset"]]["usd"] += p
                            if "Spot" not in assets[s["asset"]]["platform"] :
                                assets[s["asset"]]["platform"] += " & Spot"

        # ETHERSCAN
        balance_in_ether, balance_in_usd = get_etherscan_balance(etherscan_address, etherscan_api_key)
        if balance_in_ether > 0 :
            if not ("ETH" in assets) :
                assets["ETH"] = {"asset":"ETH", "amount":balance_in_ether, "usd":balance_in_usd, "platform":"ETHER"}
            else :
                assets["ETH"]["amount"] += balance_in_ether
                assets["ETH"]["usd"] += balance_in_usd
                if "ETHER" not in assets["ETH"]["platform"] :
                    assets["ETH"]["platform"] += " & ETHER"

            balance += balance_in_usd

        # BLOCKCHAIN.COM (BTC)
        balance_in_btc, balance_in_usd = get_blockchain_balance(btc_address)
        if balance_in_btc > 0 :
            if not ("BTC" in assets) :
                assets["BTC"] = {"asset":"BTC", "amount":balance_in_btc, "usd":balance_in_usd, "platform":"BTC"}
            else :
                assets["BTC"]["amount"] += balance_in_btc
                assets["BTC"]["usd"] += balance_in_usd
                if "BTC" not in assets["BTC"]["platform"] :
                    assets["BTC"]["platform"] += " & BTC"

            balance += balance_in_usd

    # Use AUTO saved wallet instead of API call
    else:
        for record in auto_data:
            asset = record.asset
            amount = float(record.amount)
            platform = record.platform
            usd_value = record.getUSDValue()

            # Add the asset to the assets dictionary
            if asset not in assets:
                assets[asset] = {"asset": asset, "amount": amount, "usd": usd_value, "platform": platform}
            else:
                assets[asset]["amount"] += amount
                assets[asset]["usd"] += usd_value
                assets[asset]["platform"] += f" & {platform}" if platform not in assets[asset]["platform"] else ""

            balance += usd_value

    # OTHERS WALLETS
    for record in manual_data:
        asset = record.asset
        amount = float(record.amount)
        platform = record.platform
        usd_value = record.getUSDValue()

        # Add the asset to the assets dictionary
        if asset not in assets:
            assets[asset] = {"asset": asset, "amount": amount, "usd": usd_value, "platform": platform}
        else:
            assets[asset]["amount"] += amount
            assets[asset]["usd"] += usd_value
            assets[asset]["platform"] += f" & {platform}" if platform not in assets[asset]["platform"] else ""

        balance += usd_value

    return balance, assets