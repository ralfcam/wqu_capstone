import pandas as pd
# from datetime import datetime
# import yfinance as yf

from make_sec_dataframes import rel_reports

# fil = pd.read_csv("data/releases/recent.csv", index_col="accessionNumber")[
#     ['form',
#      'ticker',
#      'reportDate',
#      'acceptanceDateTime']]

# ticks = list(fil["ticker"].unique())
# ST_DATE = "2011-01-01"
# END_DATE = datetime.now().strftime('%Y-%m-%d')

# secs = yf.download(ticks, start=ST_DATE, end=END_DATE, interval="1mo")['Adj Close']
# secs.to_csv("data/structured_prices/ticks_monthly_closing.csv")
secs = pd.read_csv("data/structured_prices/ticks_daily_closing.csv", index_col="Date")
secs.index = pd.to_datetime(secs.index, format='%Y-%m-%d')

secs_q_shifted = secs.shift(-1)
secs_q_ret = (secs_q_shifted - secs) / secs


# Function to fetch returns
# def get_next_trading_day(date):
#     # Increment the date by one day
#     next_day = date + pd.Timedelta(days=1)
#     # Check if the next day is a weekend or a holiday
#     while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
#         next_day += pd.Timedelta(days=1)
#     return next_day


def get_return(ticker, report_date, df_returns):
    try:
        # Return the returns data for the next trading day
        return df_returns.at[report_date, ticker]
    except KeyError:
        # Return None if no data is available for the next trading day
        next_trading_day = report_date + pd.Timedelta(days=1)
        return get_return(ticker, next_trading_day, df_returns)


# Example usage in a DataFrame apply function
rel_reports['following_day_return'] = rel_reports.apply(lambda row: get_return(row['ticker'],
                                                                               pd.to_datetime(row['reportDate']),
                                                                               secs_q_ret), axis=1)

rel_reports.to_csv("data/structured_prices/reports_following_day_return.csv")
