import datetime
import pandas as pd
import copy
import streamlit as st

from Portfolio import Portfolio
from Strategies.RSI import RSI
from Strategies.SMA import SMA
from Strategies.WMA import WMA
from Strategies.BollingerBands import BollingerBands
from Strategies.MACD import MACD
import plotly.express as px

pd.options.plotting.backend = 'plotly'

def simulation(portfolio, cash, end_date, progress_bar):
    ret = {}

    RSI_strategy = RSI(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), end_date)
    ret['RSI'] = RSI_strategy.simulation()
    progress_bar.progress(20)

    SMA_strategy = SMA(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), end_date)
    ret['SMA'] = SMA_strategy.simulation()
    progress_bar.progress(40)

    WMA_strategy = WMA(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), end_date)
    ret['WMA'] = WMA_strategy.simulation()
    progress_bar.progress(60)

    BollingerBands_strategy = BollingerBands(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), end_date)
    ret['BB'] = BollingerBands_strategy.simulation()
    progress_bar.progress(80)

    MACD_strategy = MACD(copy.deepcopy(portfolio), copy.deepcopy(cash), copy.deepcopy(portfolio.initial_buy_date), end_date)
    ret['MACD'] = MACD_strategy.simulation()
    progress_bar.progress(100)

    return ret

def clear_session_states():
    for fig in ['fig1', 'fig2', 'fig3']:
        st.session_state.pop(fig, None)

st.set_page_config(
    page_title="Trading Strategies", page_icon="📈"
)

st.write(
    """
# 📈 Evaluating Trading Strategies
"""
)
st.caption('by Sebastian Spector and Philipp Zeller')

today = datetime.datetime.today().date()
ETFs = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
portfolio_value = 1000000
n_ETFs = len(ETFs)
buy_date = datetime.date(2016, 1, 1)

st.write('This is a project ...')

st.write('--------------------------------------')

st.subheader('Allocation of inital portfolio')
st.write('**Selection of ETFs**:')
st.text(ETFs)
st.write('**Available cash**: ' + str(portfolio_value) + ' USD')
allocationETFs = st.slider('How much % of your initial portfolio should be invested into ETFs?', 0, 100, 70, )
allocationETFs = allocationETFs / 100

if 'allocationETFs' not in st.session_state:
    st.session_state['allocationETFs'] = allocationETFs
else:
    if st.session_state['allocationETFs'] != allocationETFs:
        clear_session_states()
        st.session_state['allocationETFs'] = allocationETFs

allocationCash = 1 - allocationETFs
cash = allocationCash * portfolio_value
st.write('**Initial portfolio allocation**')
col1, col2 = st.columns(2)
col1.metric(label = "ETFs", value = str(int(allocationETFs * 100)) + " %")
col2.metric(label = "Cash", value = str(int(allocationCash * 100)) + " %")

st.write('--------------------------------------')

st.subheader('Scenario 1')
st.caption('Time period: 01.01.2010 - Today')

if st.button('Start simulation', key = 1):
    start_date = datetime.date(2010, 1, 1)
    end_date = today

    placeholder1 = st.empty()

    with st.spinner('Initializing portfolio and buying all positions...'):
        portfolio = Portfolio(ETFs, start_date, portfolio_value, allocationETFs, cash)
        portfolio.buy_portfolio()
    placeholder1.success('Portfolio successfully initialized!')

    # Simulating five different trading strategies
    with st.spinner('Simulation is running...'):
        my_bar1 = placeholder1.progress(0)
        result = simulation(portfolio, cash, end_date, my_bar1)
    placeholder1.success('Simulation successfully finished')

    # Collecting backtesting results
    scenario_1 = [result['RSI']['Date'], result['RSI']['Total Value'], result['SMA']['Total Value'],
                  result['WMA']['Total Value'], result['BB']['Total Value'], result['MACD']['Total Value']]
    scenario_1 = pd.concat(scenario_1, axis=1, keys=['Date', 'RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'])

    # Visualizing backtesting results
    fig_1 = px.line(scenario_1, x='Date', y=['RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'],
                    title='Scenario 1: Backtesting results of different technical trading strategies',
                    labels={"variable": "Trading Strategy", "value": "Value of Portfolio"})
    fig_1.update_yaxes(gridwidth = 0.5, color='#8D8E8E')
    fig_1.update_xaxes(gridwidth = 0.5, color='#8D8E8E')

    st.session_state['fig1'] = fig_1

if 'fig1' in st.session_state:
    st.plotly_chart(st.session_state['fig1'])

st.write('--------------------------------------')

st.subheader('Scenario 2')
st.caption('Time period: 01.01.2019 - Today')

if st.button('Start simulation', key = 2):
    start_date = datetime.date(2019, 1, 1)
    end_date = today

    placeholder2 = st.empty()

    # Create initial portfolio
    with st.spinner('Initializing portfolio and buying all positions...'):
        portfolio = Portfolio(ETFs, start_date, portfolio_value, allocationETFs, cash)
        portfolio.buy_portfolio()
    placeholder2.success('Portfolio successfully initialized!')

    # Simulating five different trading strategies
    with st.spinner('Simulation is running...'):
        my_bar2 = placeholder2.progress(0)
        result = simulation(portfolio, cash, end_date, my_bar2)
    placeholder2.success('Simulation successfully finished')

    # Collecting backtesting results
    scenario_2 = [result['RSI']['Date'], result['RSI']['Total Value'], result['SMA']['Total Value'],
                  result['WMA']['Total Value'], result['BB']['Total Value'], result['MACD']['Total Value']]
    scenario_2 = pd.concat(scenario_2, axis=1, keys=['Date', 'RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'])

    # Visualizing backtesting results
    fig_2 = px.line(scenario_2, x='Date', y=['RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'],
                    title='Scenario 2: Backtesting results of different technical trading strategies',
                    labels={"variable": "Trading Strategy", "value": "Value of Portfolio"})
    fig_2.update_yaxes(gridwidth=0.5, color='#8D8E8E')
    fig_2.update_xaxes(gridwidth=0.5, color='#8D8E8E')

    st.session_state['fig2'] = fig_2

if 'fig2' in st.session_state:
    st.plotly_chart(st.session_state['fig2'])


st.write('--------------------------------------')

st.subheader('Scenario 3')
st.caption('Time period: 01.01.2021 - Today')



if st.button('Start simulation', key = 3):
    start_date = datetime.date(2021, 1, 1)
    end_date = today

    placeholder3 = st.empty()

    # Create initial portfolio
    with st.spinner('Initializing portfolio and buying all positions...'):
        portfolio = Portfolio(ETFs, start_date, portfolio_value, allocationETFs, cash)
        portfolio.buy_portfolio()
    placeholder3.success('Portfolio successfully initialized!')

    # Simulating five different trading strategies
    with st.spinner('Simulation is running...'):
        my_bar3 = placeholder3.progress(0)
        result = simulation(portfolio, cash, end_date, my_bar3)
    placeholder3.success('Simulation successfully finished')

    placeholder3.empty()

    # Collecting backtesting results
    scenario_3 = [result['RSI']['Date'], result['RSI']['Total Value'], result['SMA']['Total Value'],
                  result['WMA']['Total Value'], result['BB']['Total Value'], result['MACD']['Total Value']]
    scenario_3 = pd.concat(scenario_3, axis=1, keys=['Date', 'RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'])

    # Visualizing backtesting results
    fig_3 = px.line(scenario_3, x='Date', y=['RSI', 'SMA', 'WMA', 'BollingerBands', 'MACD'],
                    title='Scenario 3: Backtesting results of different technical trading strategies',
                    labels={"variable": "Trading Strategy", "value": "Value of Portfolio"})
    fig_3.update_yaxes(gridwidth = 0.5, color='#8D8E8E')
    fig_3.update_xaxes(gridwidth = 0.5, color='#8D8E8E')

    st.session_state['fig3'] = fig_3

if 'fig3' in st.session_state:
    st.plotly_chart(st.session_state['fig3'])