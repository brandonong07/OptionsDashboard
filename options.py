from py_vollib.black_scholes import black_scholes
from datetime import datetime, time
import zoneinfo as ZoneInfo
from decimal import Decimal, ROUND_UP

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
    
    def getMid(self):
        return round((self.bid + self.ask) / 2, 1)
    
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

    def getStrike(self):
        return self.Strike
    
    def blackScholesPrice(self):
        time_in_years = max(self.timeToClose.total_seconds() / 31536000, 0.000001)  # Avoid division by zero for expired options
        return round(black_scholes(self.OptionType[0].lower(), float(self.currentPrice), float(self.Strike), time_in_years, float(self.riskFreeRate)/ 100, float(self.impVol) / 100), 2)

    def advancedGreeks(self):
        # Working on implementing Vanna, Charm, Speed, Zomma, Color, Ultima, etc.
        time_in_years = max(self.timeToClose.total_seconds() / 31536000, 0.000001)
        time_bump = 3600 / 31536000
        t_minus_1h = max(time_in_years - time_bump, 0.000001)