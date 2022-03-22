import yfinance as yf  # library to gather financial data from https://finance.yahoo.com/
import pandas as pd  # fast and powerful data analysis and manipulation tool
import datetime
from tqdm import tqdm  # fast and extensible progress bar

tqdm.pandas()

initial_buy_date = None

# Get history of ETFs
def get_history(portfolio):
    print('Retrieving histories of all tickers ...')
    histories = portfolio['Ticker'].progress_map(lambda x: yf.Ticker(x).history(period='max', interval='1d'))
    for df in histories:
        df.reset_index(inplace=True)
        df['Date'] = df['Date'].map(lambda x: x.date())
        df.set_index('Date', inplace=True, drop=True)
    # Create dict
    ret = dict(zip(portfolio['Ticker'], histories))
    return ret


class Portfolio:
    today = datetime.datetime.today().date()

    def __init__(self, ETFs, buy_date, portfolio_value, allocation_ETFs, cash):
        self.initial_buy_date = None
        self.histories = None
        self.ETFs = ETFs
        self.n_ETFs = len(self.ETFs)
        self.buy_date = buy_date
        self.portfolio_value = portfolio_value
        self.allocation_ETFs = allocation_ETFs
        self.cash = cash
        self.default_buy = self.allocation_ETFs / len(ETFs) * self.portfolio_value
        self.portfolio = self.initialize_portfolio()

    # Assumption: no transaction cost, we can buy the ETFs for the current price
    def buy_initial_positions(self, ticker, history, buy_date, today):
        global initial_buy_date
        try:  # Check if buy_date is of type datetime
            if buy_date == today:
                initial_buy_date = buy_date
                return yf.Ticker(ticker).info['regularMarketPrice']
            elif buy_date < today:
                if buy_date in history.index.values:
                    initial_buy_date = buy_date
                    return history.loc[buy_date]['Close'].item()
                else:  # need to find the next trading day
                    idx = history.index.searchsorted(value=buy_date)
                    if 0 < idx < len(history.index):
                        initial_buy_date = history.index[idx]
                        return history['Close'].iloc[idx]
                    else:
                        print('No historical data found for given input: Ticker = {ticker} and '
                              'Buy Date = {buy_date}'.format(ticker=ticker, buy_date=buy_date))
                        self.cash += self.portfolio[self.portfolio['Ticker'] == ticker]['Value'].item()
                        self.portfolio.loc[self.portfolio.Ticker == ticker, ['Weight', 'Value', '#ofETFs']] = 0
                        return 0
            else:
                raise ValueError('Given input: "buy_date" is in the future. Either give today\'s date or a date in the '
                                 'past as input')
        except TypeError:
            raise TypeError('Input: "buy_date" must be of type <class \'pandas._libs.tslibs.timestamps.Timestamp\'>')

    def initialize_portfolio(self):
        # Initialization of our portfolio according to the weights
        weights = [self.allocation_ETFs / self.n_ETFs] * self.n_ETFs
        # Add ETFs to portfolio
        portfolio_df = pd.DataFrame(list(zip(self.ETFs, weights)), columns=['Ticker', 'Weight'])
        portfolio_df['Value'] = portfolio_df['Weight'] * self.portfolio_value
        return portfolio_df

    def buy_portfolio(self):
        self.histories = get_history(self.portfolio)
        print('Buying all positions of the initial porfolio ...')
        self.portfolio['Price'] = self.portfolio['Ticker'].progress_map(
            lambda x: self.buy_initial_positions(x, self.histories[x], self.buy_date, self.today))
        self.initial_buy_date = initial_buy_date
        self.portfolio['Date'] = initial_buy_date
        self.portfolio['#ofETFs'] = self.portfolio['Value'] / self.portfolio['Price']
        self.portfolio.fillna(0, inplace=True)
