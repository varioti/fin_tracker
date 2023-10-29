import hmac
import hashlib
import requests
import json
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

# ORDERS
def get_orders(s1, s2="BUSD", price_is_usd=True):
    symbol = s1+s2
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "symbol={}&timestamp={}".format(symbol,timestamp)
    signature = generate_signature(query_string)

    url = "{}/api/v3/allOrders?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }
    all_orders = json.loads(requests.request("GET", url, headers=headers, data=payload).text)

    # Compute quantity in usd if it's not already the case
    if not price_is_usd :
        for i in range(len(all_orders)):
            s2_price = get_price(s2)
            new_qtt = s2_price * float(all_orders[i]["cummulativeQuoteQty"])
            all_orders[i]["cummulativeQuoteQty"] = new_qtt

    return all_orders

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

def get_flexible_savings_balance(asset):
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "asset={}&timestamp={}".format(asset, timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/lending/daily/token/position?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

def get_locked_savings_balance(asset, project_id):
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "asset={}&projectId={}&status=HOLDING&timestamp={}".format(asset, project_id, timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/lending/project/position/list?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

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

def get_savings_balance():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "status=HOLDING&timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/lending/union/account?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

def get_all_earn_products():
    """ Gets all savings products from Binance """
    def get_earn_products(current_page=1):
        """ Gets 50 savings products in "current" page ...modified from source:
            https://binance-docs.github.io/apidocs/spot/en/#savings-endpoints """
        timestamp = int(time.time() * 1000 + get_timestamp_offset())
        query_string = "&current={}&status=SUBSCRIBABLE&timestamp={}".format(
                        current_page, timestamp)
        signature = generate_signature(query_string)

        url = "{}/sapi/v1/lending/daily/product/list?{}&signature={}".format(
                  uri, query_string, signature)

        payload = {}
        headers = {"Content-Type": "application/json",
                  "X-MBX-APIKEY": binance_api_key}

        result = json.loads(requests.request("GET", url, headers=headers, data=payload).text)

        return result

    all_products = []
    more_products = True
    current_page = 0

    while more_products:
        current_page += 1
        prod = get_earn_products(current_page=current_page)
        all_products.extend(prod)
        if len(prod)==50:
            more_products = True
        else:
            more_products = False

    return all_products

def get_global_balance(others={}):
    # INIT
    balance = 0
    assets = {}

    # SAVINGS
    savings = get_savings_balance()
    balance = balance + float(savings["totalAmountInUSDT"]) + float(savings["totalFixedAmountInUSDT"])
    for pos in savings["positionAmountVos"] :
        if float(pos["amount"]) > 0 and "LD" != pos["asset"][:2]:
            if not pos["asset"] in assets :
                assets[pos["asset"]] = {"asset":pos["asset"], "amount":float(pos["amount"]), "usd":float(pos["amountInUSDT"])}
            else :
                assets[pos["asset"]]["amount"] += float(pos["amount"])
                assets[pos["asset"]]["usd"] += float(pos["amountInUSDT"])

    # FUNDINGS
    fundings = get_funding_balance()
    for f in fundings :
        if not (f["free"] is None) :
            price_usd = get_price(f["asset"],"USD")
            p = float(f["free"])*price_usd
            balance += p

            if not f["asset"] in assets :
                assets[f["asset"]] = {"asset":f["asset"], "amount":float(f["free"]), "usd":p}
            else :
                assets[f["asset"]]["amount"] += float(f["free"])
                assets[f["asset"]]["usd"] += p

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
                        assets[s["asset"]] = {"asset":s["asset"], "amount":float(s["free"]), "usd":p}
                    else :
                        assets[s["asset"]]["amount"] += float(s["free"])
                        assets[s["asset"]]["usd"] += p

            if (not s["locked"] is None) and float(s["locked"]) > 0:
                price_usd = get_price(s["asset"],"USD")
                if (price_usd is not None) :
                    p = float(s["free"])*price_usd
                    balance += p
                    if not s["asset"] in assets :
                        assets[s["asset"]] = {"asset":s["asset"], "amount":float(s["locked"]), "usd":p}
                    else :
                        assets[s["asset"]]["amount"] += float(s["locked"])
                        assets[s["asset"]]["usd"] += p

    # ETHERSCAN
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={etherscan_address}&tag=latest&apikey={etherscan_api_key}"
    response = requests.get(url)
    balance_in_wei = json.loads(response.text)["result"]

    balance_in_ether = int(balance_in_wei) / 10**18 # Convert Wei to Ether (1 Ether = 10^18 Wei)
    price_usd = get_price("ETH","USD")
    balance_in_usd = balance_in_ether * price_usd
    if not ("ETH" in assets) :
        assets["ETH"] = {"asset":"ETH", "amount":balance_in_ether, "usd":balance_in_usd}
    else :
        assets["ETH"]["amount"] += balance_in_ether
        assets["ETH"]["usd"] += balance_in_usd

    balance += balance_in_usd

    # BLOCKCHAIN.COM (BTC)
    btc_url = f"https://blockchain.info/balance?active={btc_address}"

    response = requests.get(btc_url)
    balance_in_sat = int(json.loads(response.text)[btc_address]["final_balance"])
    balance_in_btc = balance_in_sat/10**8

    price_usd = get_price("BTC","USD")
    balance_in_usd = balance_in_btc * price_usd
    if not ("BTC" in assets) :
        assets["BTC"] = {"asset":"BTC", "amount":balance_in_btc, "usd":balance_in_usd}
    else :
        assets["BTC"]["amount"] += balance_in_btc
        assets["BTC"]["usd"] += balance_in_usd

    balance += balance_in_usd

    # OTHERS WALLETS
    for i in others :
        for name, asset in others[i].items():
            balance += asset["usd"]
            if not (name in assets) :
                assets[name] = {"asset":name, "amount":asset["amount"], "usd":asset["usd"]}
            else :
                assets[name]["amount"] += asset["amount"]
                assets[name]["usd"] += asset["usd"]

    return balance, assets

get_global_balance()