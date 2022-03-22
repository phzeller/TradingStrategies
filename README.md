# 📈 Evaluating Trading Strategies

In this project, we implemented five different technical analysis strategies in Python. Creating a backtesting framework has enabled us to evaluate each strategy’s performance over different time horizons. We decided to implement the following five trading strategies:

1. Relative Strength Index (RSI): 30, 70
Conservative investors tend to use RSI thresholds of 30 and 70 as trading signals, whereas more aggressive investors prefer boundary values of 20 and 80. In our implementation, we decided to use the more conservative thresholds, 30 and 70. This means, that if the RSI reaches 70, the respective stock is considered overbought, and therefore, needs to be sold. However, when the RSI falls to 30, the stock is considered oversold and thus, signals a buying recommendation.

2. Simple Moving Average (SMA): 50, 200
In this strategy, we have used the recognition of two trading patterns: the golden cross and the death cross. The golden cross occurs when the faster (50 days) SMA crosses the slower (200 days) SMA from the bottom. This is considered as a buy signal. In contrast to that, the death cross is observed when the faster SMA crosses the slower SMA from the top. In this case, it is a sell signal.

3. Weighted Moving Average (WMA): 21
The WMA is a popular indicator, which is preferably used for short-term analysis. Once the stock price crosses the WMA of the last 21 days from the bottom, it is a buy. If the stock prices fall from the top below the WMA 21, it is a sell.

4.	Bollinger Bands (BB): 20
When using the technical analysis of Bollinger Bands, three different indices are calculated. First, we determine the simple moving average (SMA) of the last 20 days. Besides that, we calculate the standard deviation above as well as below the SMA of 20 days. If the stock price touches the upper band, it is a sell signal and when it touches the lower band it is a buy. Thus, the volatility from the perspective of standard deviation determines when to buy or sell the respective stock.

5.	Moving Average Convergence Divergence (MACD): 12, 26, 9
The MACD strategy investigates the difference between two means: the faster (12 days) and the slower (26 days). These averages are exponential moving averages. The indicator is also used as the signal which is the exponential moving average between the 9-period exponential moving average and the MACD.

For each strategy, the same criteria are applied:
* Once we receive a selling sign, the entire position of the respective ETF is sold
* If the system recognizes a buying sign, the entire position in this ETF will be doubled
* Buying ETFs is only possible if enough cash is available
* As soon as a buying or selling signal is recognized, the portfolio will be rebalanced
* Transaction costs are neglected

### Implementation
The project is deployed as a Web Application on streamli.io. The Web Application allows simulation for any portfolio allocations. It is accessible @ https://share.streamlit.io/phzeller/tradingstrategies/src/Simulation.py. 
However, the project can also be run locally with streamlit or by using the respective Jupyter Notebook.

### Data sources and evaluation set-up
* Historical financial data of all 11 ETF’s: 'XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
* The initial value of the portfolio is 1 Mio. USD
* By default, we assume an initial portfolio allocation of 70% invested in ETF’s and remaining 30% are cash 
* The initial investment into ETFs is equally distributed and thus, the portfolio holds the exact same value for each of the ETFs 

### Time horizons
All five strategies were simulated for three different time horizons:
* Scenario 1: 01.01.2010 – Today
* Scenario 1: 01.01.2019 - Today
* Scenario 1: 01.01.2021 - Today
