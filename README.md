# Binance-Arbitrage-Bot

Bot that arbitrages on Binance with the goal of earning ETH 

# how it works

In multiple threads, the bot loops a three part trade sequence which is 1) buy an alt coin on the ETH market 2) sell that alt coin on the BTC market 3) buy back ETH on the BTC market, executing a type of strategy called trilateral arbitrage. It decides which alt coin to use based on current market data and a given minimum expected roi per trade. It makes all trades by placing limit orders at the current best bid. Frequently, the bot has to cancel the order corresponding to the first trade of the sequence and start over without it getting filled. This happens when it gets outbid, or the market data changes such that it no longer expects a profit from the current sequence. The other orders always get filled and this usually happens quickly.

# dependencies and use

Install the [python wrapper of the Binance API](https://github.com/sammchardy/python-binance) along with its dependencies. 
You need to copy and paste your binance api key and secret where it says `"copy and paste here"` at the top of the module, and have on Binance at least .1 ETH and some BNB for paying fees (have this option selected on your Binance account). There are four attributes that should be user-defined. See the comments under `if __name__ == "__main__":` for this. The bot doesn't print anything to the screen, though it runs outside of the main thread, so you're free to call various methods from `BinanceArbBot` and `Client` to check on it. You can also adjust the user-defined attributes except `thread_num` in real-time. Here's an example of what the shell could look like.

```
>>> bab.min_ev=1.004
>>> bab.show_value_info()
ETH value = 3.252782344038547
ETH balance = 3.1970163
BNB balance = 0.74899408
BTC balance = 1.18e-06
ETH/USD = (299.39, 299.42)
>>> client.get_open_orders()
[]
>>> client.get_open_orders()
[{'symbol': 'BQXETH', 'orderId': 19051449, 'clientOrderId': 'B8vkMzvz2vCThAUMZ9m3UU', 'price': '0.00163950', 'origQty': '75.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1534482186327, 'updateTime': 1534482186327, 'isWorking': True}, {'symbol': 'DATAETH', 'orderId': 4553749, 'clientOrderId': 'QLjbqyQ1G13FpTwhmMZp1p', 'price': '0.00010154', 'origQty': '1280.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1534482185467, 'updateTime': 1534482185467, 'isWorking': True}]
>>> bab.trade_status_dict['BQXETH']
{'e': 'executionReport', 'E': 1534482187219, 's': 'BQXETH', 'c': 'zMIGEL5nTx7BxU1TFfavpI', 'S': 'BUY', 'o': 'LIMIT', 'f': 'GTC', 'q': '75.00000000', 'p': '0.00163950', 'P': '0.00000000', 'F': '0.00000000', 'g': -1, 'C': 'B8vkMzvz2vCThAUMZ9m3UU', 'x': 'CANCELED', 'X': 'CANCELED', 'r': 'NONE', 'i': 19051449, 'l': '0.00000000', 'z': '0.00000000', 'L': '0.00000000', 'n': '0', 'N': None, 'T': 1534482187220, 't': -1, 'I': 38813163, 'w': False, 'm': False, 'M': False, 'O': 1534482186327, 'Z': '0.00000000'}
>>> client.get_open_orders()
[{'symbol': 'DOCKETH', 'orderId': 1104526, 'clientOrderId': 'YcJJdPvIWmnqYodhuK3MuL', 'price': '0.00005496', 'origQty': '390.00000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1534482229343, 'updateTime': 1534482229343, 'isWorking': True}]
>>> bab.show_value_info()
ETH value = 3.251064362740666
ETH balance = 3.19471187
BNB balance = 0.73590901
BTC balance = 4.2e-07
ETH/USD = (296.28, 296.62)
>>> bab.wait_time=4
```

# results

The bot was consistently earning about .3 ETH a day, from Jan - May 2018, until one day it suddenly started to more or less break even. This is still the case, though perhaps it could still eke out a small profit with `expected_roi` set very high (over .004) and in periods of exceptionally high volatility.

# donate

If you find the code useful, please consider donating. 

ETH: 0x4da564118a8585fd6e63a7c0066d51e7a16464d5

BTC: 146qGfUuk4Ts6avXvKh1aZer2i7b7Ey21e

LTC: LZdiBF9CkrPKL5njV22bmADKuuhhm5ZTQS
