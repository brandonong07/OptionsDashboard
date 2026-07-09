# OptionsDashboard

A Python and Streamlit options analytics dashboard for analyzing option pricing, Greeks, and risk exposure.

This project was built as part of my quantitative finance portfolio as a Statistics and Economics student at UC Davis. The goal is to turn options concepts into practical tools that help traders understand payoff structure, volatility exposure, time decay, and position risk.

## Overview

OptionsDashboard analyzes option contracts using live or structured option chain data. The dashboard calculates Black-Scholes theoretical price, standard Greeks, advanced Greeks, bid/ask/mid prices, and time-to-expiration metrics.

The project is designed to support options strategy analysis, risk management, and future backtesting features.

## Current Features

- Streamlit dashboard for options analytics
- Black-Scholes option pricing
- Bid, ask, and mid-price extraction from option chain data
- Time-to-expiration calculation using market close timing
- Standard Greeks:
  - Delta
  - Gamma
  - Theta
  - Vega
  - Rho
- Advanced Greeks:
  - Vanna
  - Charm
  - Speed
  - Vomma
- Support for calls and puts
- Risk-free rate input
- Implied volatility handling
- Foundation for scenario-based risk analysis

## Why This Project Matters

Options trading is not only about market direction. A trade can behave very differently depending on volatility, time decay, convexity, and position sizing.

This project helps break down those risks by connecting option prices and Greeks to practical trading decisions. It also gives me a stronger foundation in derivatives, Python, data analysis, and quantitative risk modeling.

## Tech Stack

- Python
- Streamlit
- pandas
- NumPy
- SciPy
- vollib
- datetime / zoneinfo
- Option chain data

## Project Structure

```text
OptionsDashboard/
├── api.py
├── dashboard.py
├── options.py
├── options_ladder.json
├── requirements.txt
└── README.md
