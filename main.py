
import flask
import hmac
import hashlib
import json
import time
import requests
from flask import Flask

app = Flask(__name__)


@app.route("/")
def main_():
    method = flask.request.args.get('method')
    #key = flask.request.args.get('key')
    #secret = flask.request.args.get('secret')
    key = "18bb0fa633edb925cff40475f8e7355961757039c9c9920a"
    secret = "e8b8aedbf8f06beefa13469e7789734866372c994c7a3ea6526d48ee3d769a6c"
    obj = ""
    global mainUrl
    mainUrl = "https://api.coindcx.com/exchange/ticker"
    global mainResponse
    mainResponse = requests.get(mainUrl)
    global currencyData
    currencyData = mainResponse.json()
    global btcinrPrice
    for each in currencyData:
        if each["market"] == "BTCINR":
            btcinrPrice = (each["last_price"]).strip('"')
            print(btcinrPrice)
            break

    if method == 'trades':
        return getTrades(key, secret)
    if method == 'balances':
        return getBalances(key, secret)
    if method == 'market':
        return getMarket(obj)


def getTrades(key, secret):
    # python3
    secret_bytes = bytes(secret, encoding='utf-8')

    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))

    body = {
        "limit": 4,
        "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators=(',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/orders/trade_history"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data=json_body, headers=headers)
    data = response.json()
    return json.dumps(data)


def getBalances(key, secret):
    # python3
    secret_bytes = bytes(secret, encoding='utf-8')

    # Generating a timestamp
    timeStamp = int(round(time.time() * 1000))

    body = {
        "timestamp": timeStamp
    }

    json_body = json.dumps(body, separators=(',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    url = "https://api.coindcx.com/exchange/v1/users/balances"
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data=json_body, headers=headers)
    json_data_list = []

    myString = "<table>"
    myString += "<tr><th>Currency</th><th>Value</th><th>Value in BTC</th><th>Value in INR</th><th>Investment today in INR</th></tr>"
    currencyName =""
    currencyBalance =""
    priceInBTC =""
    priceInINR =""
    investmentTodayINR =""
    totalInvestment = 0
    average = 0
    for each in response.json():
        if each["balance"] != '0.0':
            json_data_list.append(each)
            myString += "<div>"
            myString += "<tr>"
            myString += "<td>"
            currencyName = json.dumps(each["currency"]).strip('"')
            myString += currencyName
            myString += "</td>"
            myString += "<td>"
            currencyBalance = json.dumps(each["balance"]).strip('"')
            myString += currencyBalance
            myString += "</td>"
            myString += "<td>"
            priceInBTC = getMarket(currencyName).strip('"')
            myString += priceInBTC
            myString += "</td>"
            myString += "<td>"
            if priceInBTC != 'NA':
                if currencyName == "USDT":
                    for each in currencyData:
                        if each["market"]=="USDTINR":
                            priceInINR = str(each["last_price"])
                else:
                    priceInINR = float(priceInBTC)*float(btcinrPrice)
            elif currencyName == "INR":
                priceInINR = 1
            elif currencyName == "BTT" or currencyName == "TUSD":
                usdttoinr = 0
                for each in currencyData:
                    if each["market"] == "USDTINR":
                        usdttoinr = float(str(each["last_price"]))
                        break
                if currencyName == "BTT":
                    for each in currencyData:
                        if each["market"] == "BTTUSDT":
                            priceInINR = str(float(each["last_price"])*usdttoinr)
                            break
                elif currencyName == "TUSD":
                    for each in currencyData:
                        if each["market"] == "TUSDUSDT":
                            priceInINR = str(float(each["last_price"])*usdttoinr)
                            break
            myString += str(priceInINR)
            myString += "</td>"
            myString += "<td>"
            investmentTodayINR = float(currencyBalance)*float(priceInINR)
            totalInvestment += investmentTodayINR
            myString += "<b>"
            myString += str(investmentTodayINR)
            myString += "</b>"
            myString += "</td>"
            myString += "</tr>"
            myString += "</div>"
    myString += "</table><br/>"
    myString += "<b>Total Capital: Rs "+str(totalInvestment)+"</b>"

#    return json.dumps(json_data_list) + myString
#    getMarket(currencyName)
    return myString


def getMarket(currencyName):

    price = "NA"
    for each in currencyData:
        if currencyName == "BTC":
            return str(1)
        elif currencyName == "USDT":
            for a in currencyData:
                if a["market"] == "BTCUSDT":
                    return str(a["last_price"])
        elif each["market"] == currencyName+"BTC":
            price = str(each["last_price"])
            break

    return json.dumps(price)


if __name__ == "__main__": app.run();
