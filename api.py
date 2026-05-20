from datetime import date, datetime, time
from http import client
from urllib import response
import zoneinfo as ZoneInfo
import yfinance as yf
import schwabdev
import os
import pandas as pd
from py_vollib.black_scholes import black_scholes
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
    def __init__(self, Strike, ExpDate, OptionType, data, RFR):
        map_key = "callExpDateMap" if OptionType == "CALL" else "putExpDateMap"
        
        # TIME CALCULATION 
        est_tz = ZoneInfo.ZoneInfo("America/New_York")
        est_now = datetime.now(est_tz)
        
        # 1. Create a datetime for exactly 4:00 PM EST on Expiration Day
        exp_datetime = datetime.combine(ExpDate, time(16, 0), tzinfo=est_tz)
        
        # 2. Total precise time left for Black-Scholes
        self.timeToClose = exp_datetime - est_now
        
        # 3. Calendar days left for the Schwab JSON key
        self.days_to_exp = (ExpDate - est_now.date()).days

        # MAP NAVIGATOR
        nav = data[map_key][f"{ExpDate}:{self.days_to_exp}"][Strike][0]

        self.Strike = Strike
        self.ExpDate = ExpDate
        self.OptionType = OptionType
        self.currentPrice = data['underlyingPrice']
        
        self.bid = nav['bid']
        self.ask = nav['ask']
        self.delta = nav['delta']
        self.gamma = nav['gamma']
        self.theta = nav['theta']
        self.vega = nav['vega']
        self.rho = nav['rho']
        self.impVol = nav['volatility']
        
        self.riskFreeRate = RFR
    
    def getCurrentPrice(self):
        return self.currentPrice
    
    def getBid(self):
        return self.bid
    
    def getAsk(self):
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
        time_in_years = max(self.timeToClose.total_seconds() / 31536000, 0.000001)  # Avoid division by zero for expired options
        return black_scholes(self.OptionType[0].lower(), float(self.currentPrice), float(self.Strike), time_in_years, float(self.riskFreeRate)/ 100, float(self.impVol) / 100)

    def advancedGreeks(self):
        # Working on implementing Vanna, Charm, Speed, Zomma, Color, Ultima, etc.
        time_in_years = max(self.timeToClose.total_seconds() / 31536000, 0.000001)
        time_bump = 3600 / 31536000
        t_minus_1h = max(time_in_years - time_bump, 0.000001)
        
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
        includeUnderlyingQuote=True
    )

    # Best practice: Check if the response is valid before parsing JSON
    if response is not None and response.ok:
        data = response.json()

        # Format: "STRIKE, add .0 to end, ExpDate, OptionType, data"
        rate = get_risk_free_rate()

        SPXOption = Option("7500.0", date(2026, 5, 15), "CALL", data, rate)
        print(f"Current Price: {SPXOption.getCurrentPrice()}")
        print(f"Bid: {SPXOption.getBid()}")
        print(f"Ask: {SPXOption.getAsk()}")
        print(f"Black-Scholes Price: {SPXOption.blackScholesPrice()}")
        # SPXOption2 = Option("7505.0", date(2026, 5, 15), "PUT", data)

        
    else:
        print("API Request Failed. Response was:", response) 


if __name__ == "__main__":
    main()