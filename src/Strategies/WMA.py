import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm  # fast and extensible progress bar

from Strategies.Strategy import Strategy


# WMA 21 (short term), when the price crosses from below the WMA 21 it is a buy,
# when it crosses from above it's a sell.
class WMA(Strategy):
    days = 21
    weights = np.empty(shape=(0, 0))
    for i in range(days, 0, -1):
        weights = np.append(weights, i)
    weights = weights / np.sum(weights)

    def __init__(self, portfolio, cash, start_date, end_date):
        super().__init__(portfolio, cash, start_date, end_date)

    def calculate_WMA(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['WMA' + str(self.days)] = history['Close'].rolling(window=self.days).apply(
                lambda x: np.sum(self.weights * x), raw=False)
        return histories

    def buy(self, price, current_stock_count):
        return super().buy(price, current_stock_count)

    def sell(self, price, current_stock_count):
        return super().sell(price, current_stock_count)

    def calculate_signals(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['Signal'] = np.where(history['WMA' + str(self.days)] > history['Close'], 1, 0)
            history['Diff'] = history['Signal'].diff()
        return histories

    def determine_action(self, history, day):
        row = history.loc[day]
        if row['Diff'] > 0:
            return 'buy'
        elif row['Diff'] < 0:
            return 'sell'
        else:
            return 'no action'

    def update_portfolio(self, portfolio, cash, histories, transactions, day):
        return super().update_portfolio(portfolio, cash, histories, transactions, day)

    def simulation(self):
        history = []
        self.portfolio.histories = self.calculate_WMA(self.portfolio.histories)
        self.portfolio.histories = self.calculate_signals(self.portfolio.histories)

        date_range = pd.Series(pd.date_range(start=self.start_date, end=self.end_date)
                               .to_pydatetime()).map(lambda x: x.date())
        print('Simulation for WMA simulation is running ...')
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
