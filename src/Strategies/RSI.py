import pandas as pd
import pandas_ta as pta  # calculate RSI
import datetime
from tqdm import tqdm  # fast and extensible progress bar

from Strategies.Strategy import Strategy


class RSI(Strategy):

    def __init__(self, portfolio, cash, start_date, end_date):
        super().__init__(portfolio, cash, start_date, end_date)

    # 1) RSI (30-70 range): Whenever the RSI touches 30 from the above it´s a buy, when it touches 70
    # is a sell. We are going to rebalance each time one of the 11 ETF´s touches 30 or 70. We add or subtract 5%
    def calculate_rsi(self, histories):
        for ticker in histories:
            history = histories[ticker]
            history['RSI'] = pta.rsi(history['Close'])
            history['prev_RSI'] = history.shift(1)['RSI']
        return histories

    def buy(self, price, current_stock_count):
        return super().buy(price, current_stock_count)

    def sell(self, price, current_stock_count):
        return super().sell(price, current_stock_count)

    def determine_action(self, history, day):
        row = history.loc[day]
        if row['prev_RSI'] < row['RSI'] and row['RSI'] >= 70 and row['prev_RSI'] < 70:  # sell ETF
            return 'sell'
        elif row['prev_RSI'] > row['RSI'] and row['RSI'] <= 30 and row['prev_RSI'] > 30:  # buy ETF
            return 'buy'
        else:
            return 'no action'

    def update_portfolio(self, portfolio, cash, histories, transactions, day):
        return super().update_portfolio(portfolio, cash, histories, transactions, day)

    def simulation(self):
        history = []
        self.portfolio.histories = self.calculate_rsi(self.portfolio.histories)

        date_range = pd.Series(pd.date_range(start=self.start_date, end=self.end_date)
                               .to_pydatetime()).map(lambda x: x.date())
        print('Simulation for RSI simulation is running ...')
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
