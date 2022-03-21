import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm  # fast and extensible progress bar

from Strategies.Strategy import Strategy

# Bollinger bands: Bottom-Top ranges for the stock price
class BollingerBands(Strategy):
    days = 20

    def __init__(self, portfolio, cash, start_date, end_date):
        super().__init__(portfolio, cash, start_date, end_date)

    def calculate_BollingerBands(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['SMA' + str(self.days)] = history['Close'].rolling(window=self.days).mean()
            history['std'] = history['Close'].rolling(window=self.days).std(ddof=0)
            history['upper_BB'] = history['SMA' + str(self.days)] + history['std'] * 2
            history['lower_BB'] = history['SMA' + str(self.days)] - history['std'] * 2
        return histories

    def buy(self, price, current_stock_count):
        return super().buy(price, current_stock_count)

    def sell(self, price, current_stock_count):
        return super().sell(price, current_stock_count)

    def calculate_signals(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['sig_upper_BB'] = np.where(history['Close'] >= history['upper_BB'], 1, 0)
            history['sig_lower_BB'] = np.where(history['lower_BB'] >= history['Close'], 1, 0)
            history['diff_upper_BB'] = history['sig_upper_BB'].diff()
            history['diff_lower_BB'] = history['sig_lower_BB'].diff()
        return histories

    def determine_action(self, history, day):
        row = history.loc[day]
        if row['diff_upper_BB'] > 0:
            return 'sell'
        elif row['diff_lower_BB'] > 0:
            return 'buy'
        else:
            return 'no action'

    def update_portfolio(self, portfolio, cash, histories, transactions, day):
        return super().update_portfolio(portfolio, cash, histories, transactions, day)

    def simulation(self):
        history = []
        self.portfolio.histories = self.calculate_BollingerBands(self.portfolio.histories)
        self.portfolio.histories = self.calculate_signals(self.portfolio.histories)

        date_range = pd.Series(pd.date_range(start=self.start_date, end=self.end_date)
                               .to_pydatetime()).map(lambda x: x.date())
        print('Simulation for Bollinger Bands simulation is running ...')
        for day in tqdm(date_range):
            transactions = {}
            for ticker in self.portfolio.portfolio['Ticker']:
                if not super().trading_day(self.portfolio.histories[ticker], day):  # skip any non-trading days
                    continue
                transactions[ticker] = self.determine_action(self.portfolio.histories[ticker], day)

            if len(transactions) > 0:
                self.portfolio.portfolio, self.portfolio.cash, self.portfolio.portfolio_value = self.update_portfolio(
                    self.portfolio.portfolio, self.portfolio.cash, self.portfolio.histories, transactions, day)
                history.append([day, self.portfolio.portfolio['Ticker'], self.portfolio.portfolio['Weight'],
                                self.portfolio.portfolio['Value'], self.portfolio.portfolio['Price'],
                                self.portfolio.portfolio['#ofETFs'], self.portfolio.portfolio_value])
            day += datetime.timedelta(days=1)

        simulation_history = pd.DataFrame(data=history,
                                          columns=['Date', 'Ticker', 'Weight', 'Value', 'Price', '#ofETFs',
                                                   'Total Value'])

        return simulation_history
