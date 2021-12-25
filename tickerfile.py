import yfinance as yf
import requests


def get_ticker(i):
    with requests.Session() as session:
        return yf.Ticker(i, session=session).info
