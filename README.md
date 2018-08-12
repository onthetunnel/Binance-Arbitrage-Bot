# Binance-Arbitrage-Bot

Bot that arbitrages between the ETH and BTC markets on Binance with the goal of winning ETH. 

# how it works

In multiple threads, it loops a three part trade sequence which is 1) buy an alt coin on ETH market 2) sell that alt coin on BTC market 3) buy back ETH on BTC market. It decides which alt coin to use based on current market data and user defined minimum expected roi per trade (see 'get_pivot' method of the 'BinanceArbBot' class). It makes all trades by placing limit orders at the current best bid. Normally, the bot has to cancel the order corresponding to the first trade of the sequence and start over without it getting filled. This happens when it gets outbid, or the market data changes such that it no longer expects a profit from the current sequence. The other trades usually execute quickly, however, and the bot ensures that their corresponding orders get filled, so its not left with extra alt coins or BTC.

# dependencies and use

[python wrapper of the Binance API](https://github.com/sammchardy/python-binance) , along with its dependencies. 
Also need to copy and paste binance api key and secret into the module,  and have on Binance have ETH and BNB, and have the BNB option for paying fees selected. For guidelines and an example of how to run the script, see the portion of code following `if __name__ == "__main__":`.
