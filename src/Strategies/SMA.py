import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm  # fast and extensible progress bar

from Strategies.Strategy import Strategy


# SMA (Smooth moving average) 50 & 200: Crossover strategy, when the shortest moving average crosses the longest one
# from the below, it´s a buy, and when it crosses from the above it´s a sell. We are going to rebalance each time
# there is a crossover in one of the ETF´s.

class SMA(Strategy):
    short_days = 50
    long_days = 200

    def __init__(self, portfolio, cash, start_date, end_date):
        super().__init__(portfolio, cash, start_date, end_date)

    def calculate_SMA(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['SMA_'+str(self.short_days)] = history['Close'].rolling(window=self.short_days).mean()
            history['SMA_'+str(self.long_days)] = history['Close'].rolling(window=self.long_days).mean()
        return histories

    def buy(self, price, current_stock_count):
        return super().buy(price, current_stock_count)

    def sell(self, price, current_stock_count):
        return super().sell(price, current_stock_count)

    def calculate_signals(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['Signal'] = np.where(history['SMA_50'] >= history['SMA_200'], 1, 0)
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
        self.portfolio.histories = self.calculate_SMA(self.portfolio.histories)
        self.portfolio.histories = self.calculate_signals(self.portfolio.histories)

        date_range = pd.Series(pd.date_range(start=self.start_date, end=self.end_date)
                               .to_pydatetime()).map(lambda x: x.date())
        print('Simulation for SMA simulation is running ...')
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
