import yfinance as yf
import scipy.stats as stats
import matplotlib as mpl
import matplotlib.pyplot as plt

def main():
    spx = yf.Ticker("^SPX")
    history = spx.history(period="1d", interval="1m")
    print(history)
    ewm20 = history['Close'].ewm(span=20, adjust=False).mean()
    std_pt = history['Close'].rolling(window=20).std()
    meanReversionLower = history['Close'] - 1*std_pt
    meanReversionUpper = history['Close'] + 1*std_pt
    print(meanReversionLower)
    print(meanReversionUpper)

    # This is kind of meaningless, it predicts in moment and not as a forward-looking indicator?
    plt.title("SPX 1-Minute Close with Mean Reversion Bands")

    plt.plot(meanReversionLower, color='red')
    plt.plot(history['Close'], color= 'black')
    plt.plot(meanReversionUpper, color='blue')

    plt.show()

if __name__ == "__main__":
    main()
