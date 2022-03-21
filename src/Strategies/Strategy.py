from abc import ABCMeta, abstractmethod
import pandas as pd

class Strategy(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, portfolio, cash, start_date, end_date):
        self.portfolio = portfolio
        self.cash = cash
        self.start_date = start_date
        self.end_date = end_date

    def trading_day(self, history, day):
        return day in history.index.values

    @abstractmethod
    def simulation(self):
        raise NotImplementedError("Method not yet implemented")

    def buy(self, price, current_stock_count):
        if pd.isna(current_stock_count):
            buy_target = self.portfolio.default_buy / price
            current_stock_count = 0
        elif current_stock_count == 0 or pd.isna(current_stock_count):
            buy_target = self.portfolio.default_buy / price
        else:
            buy_target = current_stock_count
        if self.portfolio.cash > price * buy_target:
            new_stock_count = current_stock_count + buy_target
            expense = price * buy_target
            return new_stock_count, expense
        else:
            new_stock_count = current_stock_count + (self.portfolio.cash / price)
            expense = (new_stock_count - current_stock_count) * price
            return new_stock_count, expense

    def sell(self, price, current_stock_count):
        total_selling_price = price * current_stock_count
        return total_selling_price

    def update_portfolio(self, portfolio, cash, histories, transactions, day):
        for ticker in transactions:
            hist = histories[ticker]
            price = hist.loc[day]['Close'].item()
            stock_count = portfolio[portfolio['Ticker'] == ticker]['#ofETFs'].item()
            if transactions[ticker] == 'no action':  # just update price
                portfolio.loc[portfolio['Ticker'] == ticker, ['Price']] = price
            elif transactions[ticker] == 'buy':
                if cash == 0:  # no buy possible, just update price
                    portfolio.loc[portfolio['Ticker'] == ticker, ['Price']] = price
                else:
                    number_of_shares, expense = self.buy(price, stock_count)
                    portfolio.loc[portfolio['Ticker'] == ticker, ['#ofETFs']] = number_of_shares
                    portfolio.loc[portfolio['Ticker'] == ticker, ['Price']] = price
                    cash -= expense
            elif transactions[ticker] == 'sell':
                income = self.sell(price, stock_count)
                portfolio.loc[portfolio['Ticker'] == ticker, ['#ofETFs']] = 0
                portfolio.loc[portfolio['Ticker'] == ticker, ['Price']] = price
                cash += income

        portfolio['Date'] = day  # Update Date
        portfolio['Value'] = portfolio['Price'] * portfolio['#ofETFs']  # Update Value
        total_value = cash + sum(portfolio['Value'])
        portfolio['Weight'] = portfolio['Value'] / total_value  # Update Weight
        return portfolio, cash, total_value
