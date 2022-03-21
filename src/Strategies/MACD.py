import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm  # fast and extensible progress bar

from Strategies.Strategy import Strategy


class MACD(Strategy):
    short_days = 12
    long_days = 26
    smoothing_days = 9

    def __init__(self, portfolio, cash, start_date, end_date):
        super().__init__(portfolio, cash, start_date, end_date)

    def calculate_MACD(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['EMA' + str(self.short_days)] = history['Close'].ewm(span=self.short_days, adjust=False).mean()
            history['EMA' + str(self.long_days)] = history['Close'].ewm(span=self.long_days, adjust=False).mean()
            history['MACD'] = history['EMA' + str(self.short_days)] - history['EMA' + str(self.long_days)]
        return histories

    def buy(self, price, current_stock_count):
        return super().buy(price, current_stock_count)

    def sell(self, price, current_stock_count):
        return super().sell(price, current_stock_count)

    def calculate_signals(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['Signal_line'] = history['MACD'].ewm(span=self.smoothing_days, adjust=False).mean()
            history['Signal'] = np.where(history['MACD'] >= history['Signal_line'], 1, 0)
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
        self.portfolio.histories = self.calculate_MACD(self.portfolio.histories)
        self.portfolio.histories = self.calculate_signals(self.portfolio.histories)

        date_range = pd.Series(pd.date_range(start=self.start_date, end=self.end_date)
                               .to_pydatetime()).map(lambda x: x.date())
        print('Simulation for MACD simulation is running ...')
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
