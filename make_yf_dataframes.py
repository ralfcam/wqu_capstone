import pandas as pd
from datetime import datetime
import yfinance as yf

fil = pd.read_csv("/content/recent.csv", index_col="accessionNumber")[['form', 'ticker', 'reportDate', 'acceptanceDateTime']]
ticks = list(fil["ticker"].unique())
ST_DATE = "2011-01-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')

secs = yf.download(ticks, start=ST_DATE, end=END_DATE, interval="1d")['Adj Close']
