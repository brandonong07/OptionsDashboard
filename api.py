from datetime import date
from http import client
from urllib import response

import schwabdev
import os
import requests
import pandas as pd
from dotenv import load_dotenv

def createClient(key, secret, url):
    client = schwabdev.Client(
        app_key=key,
        app_secret=secret,
        callback_url=url,
        tokens_db="~/.schwabdev/tokens.db",
        encryption=None,
        timeout=10,
        call_on_auth=None,
        open_browser_for_auth=True,
    )
    pass

    return client
def gatherOptionStats(Strike, ExpDate, OptionType, data):
    # ["call/put ExpDateMap"]["Date:Interval"]["Strike"]["0"]["Stat"]
    map = "callExpDateMap" if OptionType == "CALL" else "putExpDateMap"
    greeksList = []
    delta = data[map]
    gamma = ""
    theta = ""
    vega = ""
    rho = ""
    
    greeksList.append(delta)
    greeksList.append(gamma)
    greeksList.append(theta)
    greeksList.append(vega)
    greeksList.append(rho)
    greeksList.append(Strike)
    
    pass

def main():
    load_dotenv()  # Loads variables from .env into os.environ
    app_key = os.getenv("app_key")
    app_secret = os.getenv("app_secret")
    url = os.getenv("url")
    client = createClient(app_key, app_secret, url)

    # Testing Client
    # Pass parameters explicitly to avoid mapping errors
    response = client.option_chains(
        "$SPX",
        strategy="SINGLE",
        contractType="ALL",
        strikeCount=5, # Grabs 5 CALLS/PUTS, dependent on range (ITM, OTM, ATM) 
        fromDate=date.today(),
        toDate=date.today(),
        range="ITM",
        includeUnderlyingQuote=False
    )

    # Best practice: Check if the response is valid before parsing JSON
    if response is not None and response.ok:
        data = response.json()
        print(f"Gamma: {data['callExpDateMap']['2026-05-15:1']['7505.0'][0]['gamma']}")
    else:
        print("API Request Failed. Response was:", response) 

if __name__ == "__main__":
    main()