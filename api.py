from datetime import date, datetime, time
from http import client
import json
from urllib import response
import options as option
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
    history = irx.history(period="3d")
    latest_yield = history['Close'].iloc[-1]
    
    # Convert to decimal for your math models
    return latest_yield / 100

def main():
    load_dotenv()
    # Grab the values and force-strip any rogue quotes or spaces
    app_key = os.getenv("app_key").strip('"' "' ")
    app_secret = os.getenv("app_secret").strip('"' "' ")
    url = os.getenv("url").strip('"' "' ")

    # Ensure the https:// check passes perfectly on Windows too
    if not url.startswith("https://"):
        url = f"https://{url}"
    
    client = createClient(app_key, app_secret, url)

    # Testing Client
    # Pass parameters explicitly to avoid mapping errors
    
    response = client.option_chains(
        "$SPX",
        strategy="SINGLE",
        contractType="ALL",
        strikeCount=5, # Grabs 5 CALLS/PUTS, dependent on range (ITM, OTM, ATM) 
        fromDate="2026-06-01", # replace with date.today() later
        toDate="2026-06-01", # replace with date.today() later
        range="ITM",
        includeUnderlyingQuote=True
    )

    # Best practice: Check if the response is valid before parsing JSON
    if response is not None and response.ok:
        data = response.json()
        call_prices = list(data["callExpDateMap"]["2026-06-01:0"].keys())
        put_prices = list(data["putExpDateMap"]["2026-06-01:0"].keys())
        rate = get_risk_free_rate()
        
        # Format: "STRIKE, add .0 to end, ExpDate, OptionType, data"
        optionsLadder = []
        for strike in call_prices:
            opt = option.Option(strike, date(2026, 6, 1), "CALL", data, rate)
            adv = opt.getAdvancedGreeks()
            optionsLadder.append({
                "Direction": opt.getOptionType(),
                "Strike": float(opt.getStrike()),
                "Underlying": float(opt.getUnderlyingPrice()),
                "Bid" : float(opt.getBid()),
                "Ask" : float(opt.getAsk()),
                "IV" : float(opt.getIV()),
                "Delta" : float(opt.getDelta()),
                "Gamma" : float(opt.getGamma()),
                "Theta" : float(opt.getTheta()),
                "Scholes" : float(opt.blackScholesPrice()),
                "Vanna": float(adv["vanna"]),
                "Charm": float(adv["charm"]),
                "Speed": float(adv["speed"]),
                "Vomma": float(adv["vomma"]),
                "Vanna_1%_IV": float(adv["vanna_1%_IV"]),
                "Charm_per_hour": float(adv["charm_per_hour"]),
                "Speed_10pt": float(adv["speed_10pt"]),
                "Vomma_1%_IV": float(adv["vomma_1%_IV"])
            })
        for strike in put_prices:
            opt = option.Option(strike, date(2026, 6, 1), "PUT", data, rate)
            adv = opt.getAdvancedGreeks()
            optionsLadder.append({
                "Direction": opt.getOptionType(),
                "Strike": float(opt.getStrike()),
                "Underlying": float(opt.getUnderlyingPrice()),
                "Bid" : float(opt.getBid()),
                "Ask" : float(opt.getAsk()),
                "IV" : float(opt.getIV()),
                "Delta" : float(opt.getDelta()),
                "Gamma" : float(opt.getGamma()),
                "Theta" : float(opt.getTheta()),
                "Scholes" : float(opt.blackScholesPrice()),
                "Vanna": float(adv["vanna"]),
                "Charm": float(adv["charm"]),
                "Speed": float(adv["speed"]),
                "Vomma": float(adv["vomma"]),
                "Vanna_1%_IV": float(adv["vanna_1%_IV"]),
                "Charm_per_hour": float(adv["charm_per_hour"]),
                "Speed_10pt": float(adv["speed_10pt"]),
                "Vomma_1%_IV": float(adv["vomma_1%_IV"])
            })
        
        df = pd.DataFrame(optionsLadder)
        df.to_json("options_ladder.json", orient="records", indent=4)
        print("json created")

    else:
        print("API Request Failed. Response was:", response) 


if __name__ == "__main__":
    main()