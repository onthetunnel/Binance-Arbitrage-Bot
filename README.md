# Binance-Arbitrage-Bot

Bot that arbitrages between the ETH and BTC markets on Binance with the goal of winning ETH. 

# how it works

In multiple threads, the bot loops a three part trade sequence which is 1) buy an alt coin on the ETH market 2) sell that alt coin on the BTC market 3) buy back ETH on the BTC market, executing a type of strategy called trilateral arbitrage. It decides which alt coin to use based on current market data and a given minimum expected roi per trade (see `get_pivot` method of the `BinanceArbBot` class). It makes all trades by placing limit orders at the current best bid. Normally, the bot has to cancel the order corresponding to the first trade of the sequence and start over without it getting filled. This happens when it gets outbid, or the market data changes such that it no longer expects a profit from the current sequence. The other trades usually execute quickly, however, and the their corresponding orders should always get filled.

# dependencies and use

[python wrapper of the Binance API](https://github.com/sammchardy/python-binance) along with its dependencies. 
You need to copy and paste your binance api key and secret into where it says `"copy and paste here"` at the top of the module, and have on Binance at least .1 ETH and some BNB for paying fees (have this option selected on your Binance account). To see how to get the bot running, see the of code `if __name__ == "__main__":`. 

# results

This bot was earning about .3 ETH a day, from Jan - April of this year. The code, though, still has useful features and mostly could be used for any bot on Binance, regardless of trading strategy. In its current form, it's unlikely to lose and could still eke out a profit in periods of exceptional volatility with the parameter `expected_roi` set very high (over .004). 
