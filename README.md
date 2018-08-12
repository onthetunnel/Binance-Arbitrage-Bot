# Binance-Arbitrage-Bot

Bot that arbitrages between the ETH and BTC markets on Binance. In multiple threads, it loops a three part trade sequence which is 1) buy an alt coin on ETH market 2) sell that alt coin on BTC market 3) buy back ETH on BTC market. It decides which alt coin to use based on current market data and user defined minimum expected roi per trade. 

# dependencies
[python wrapper of the Binance API] (https://github.com/sammchardy/python-binance), along with its dependencies. 
