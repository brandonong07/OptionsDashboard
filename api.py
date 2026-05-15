from datetime import date, datetime
from http import client
from urllib import response
import zoneinfo as ZoneInfo
import yfinance as yf
import schwabdev
import os
import requests
import pandas as pd
import py_vollib as pv
from dotenv import load_dotenv
import data

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

    return client

def get_risk_free_rate():
    # ^IRX is the universal Yahoo ticker for the 13-week T-Bill
    irx = yf.Ticker("^IRX")
    
    # Get the most recent daily close
    history = irx.history(period="1d")
    latest_yield = history['Close'].iloc[-1]
    
    # Convert to decimal for your math models
    return latest_yield / 100

class Option:
    def __init__(self, Strike, ExpDate, OptionType, data):
        map = "callExpDateMap" if OptionType == "CALL" else "putExpDateMap"
        est_time = datetime.now(ZoneInfo.ZoneInfo("America/New_York"))

        dateDelta = ExpDate - est_time.date()

        self.Strike = Strike
        self.ExpDate = ExpDate
        self.OptionType = OptionType
        
        self.bid = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['bid']
        self.ask = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['ask']
        self.delta = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['delta']
        self.gamma = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['gamma']
        self.theta = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['theta']
        self.vega = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['vega']
        self.rho = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['rho']
        self.impVol = data[map][f"{ExpDate}:{dateDelta.days}"][self.Strike][0]['volatility']
        
        self.riskFreeRate = get_risk_free_rate()
    def returnBid(self):
        return self.bid
    
    def returnAsk(self):
        return self.ask
    
    # Delta: How much price will change for a $1 change in the ticker
    # Also, the probability of expiring ITM (for CALLS, OTM for PUTS)
    def getDelta(self):
        return self.delta
    
    # Gamma: How much delta will change for a $1 change in the ticker
    # Larger closer to expiration, higher gamma (delta changes more rapidly)
    def getGamma(self):
        return self.gamma
    
    # Theta: How much price will change for a 1 day change in time to expiration
    # Time decay, very important for 0DTE options
    def getTheta(self):
        return self.theta
    
    # Vega: How much price will change for a 1% change in volatility
    # Sensitivity to volatility
    def getVega(self):
        return self.vega
    
    # Rho: How much price will change for a 1% change in interest rates
    # Not relevant for 0DTE options
    def getRho(self):
        return self.rho
    
    # To use in pricing models, divide by 100 to get decimal form.
    def getImpVol(self):
        return self.impVol
    
    def getRiskFreeRate(self):
        return self.riskFreeRate

    def blackScholesPrice(self):

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
        fromDate="2026-05-15", # replace with date.today() later
        toDate="2026-05-15",
        range="ITM",
        includeUnderlyingQuote=False
    )

    # Best practice: Check if the response is valid before parsing JSON
    if response is not None and response.ok:
        data = response.json()

        # Format: "STRIKE, add .0 to end, ExpDate, OptionType, data"

        SPXOption = Option("7505.0", date(2026, 5, 15), "CALL", data)
        SPXOption.getRiskFreeRate()
        # SPXOption2 = Option("7505.0", date(2026, 5, 15), "PUT", data)

        print(f"Implied Volatility: {SPXOption.getImpVol()}")
    else:
        print("API Request Failed. Response was:", response) 


if __name__ == "__main__":
    main()