import datetime
import pandas as pd
import copy

from Portfolio import Portfolio
from Strategies.RSI import RSI
from Strategies.SMA import SMA
from Strategies.WMA import WMA
from Strategies.BollingerBands import BollingerBands
from Strategies.MACD import MACD
import plotly.express as px

today = datetime.datetime.today().date()
ETFs = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
n_ETFs = len(ETFs)
buy_date = datetime.date(2016, 1, 1)

# TODO: Idea: let the user choose the input values (-> Thus, we can make less mistakes)
# Our chosen initial allocation is 70% equally invested in ETFs and 30% cash
portfolio_value = 1000000
allocationETFs = 0.7
allocationCash = 1 - allocationETFs
cash = allocationCash * portfolio_value

portfolio = Portfolio(ETFs, buy_date, portfolio_value, allocationETFs, cash)
portfolio.buy_portfolio()

pseudo_day = datetime.date(2022, 1, 1)

RSI_strategy = RSI(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), pseudo_day)
RSI_sim_history = RSI_strategy.simulation()

SMA_strategy = SMA(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), pseudo_day)
SMA_sim_history = SMA_strategy.simulation()

WMA_strategy = WMA(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), pseudo_day)
WMA_sim_history = WMA_strategy.simulation()

BollingerBands_strategy = BollingerBands(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), pseudo_day)
BollingerBangs_sim_history = BollingerBands_strategy.simulation()

MACD_strategy = MACD(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), pseudo_day)
MACD_sim_history = MACD_strategy.simulation()

total_portfolio_values = [RSI_sim_history['Date'], RSI_sim_history['Total Value'], SMA_sim_history['Total Value'], WMA_sim_history['Total Value'], BollingerBangs_sim_history['Total Value'], MACD_sim_history['Total Value']]
total_portfolio_values = pd.concat(total_portfolio_values, axis=1, keys=['Date', 'RSI', 'SMA', 'WMA', 'BollingerBangs', 'MACD'])

# #Visualization
# #Plot:
pd.options.plotting.backend = 'plotly'
fig = px.line(total_portfolio_values, x='Date', y=['RSI', 'SMA', 'WMA', 'BollingerBangs', 'MACD'], 
    title='Backtesting results of different technical trading strategies', 
    labels={"variable": "Trading Strategy", "value": "Value of Portfolio"})
fig.show()