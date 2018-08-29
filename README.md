# Binance-Arbitrage-Bot

Bot that arbitrages on Binance with the goal of earning ETH 

# how it works

In multiple threads, the bot loops a three part trade sequence which is 1) buy an alt coin on the ETH market 2) sell that alt coin on the BTC market 3) buy back ETH on the BTC market, executing a type of strategy called trilateral arbitrage. It makes all trades by initally placing limit orders at the best bid price. For each alt coin common to both ETH and BTC markets, it calculates an ROI for the sequence using the best bid price for the first two orders, and the best ask price for the last one, and then chooses whichever alt coin not being used in any current orders yields the highest ROI, provided that ROI is at least as high as a minimum ROI that's defined by the user. The amount of the alt coin used is the lesser of an equivalent amount to a user-defined maximum ETH amount and the volume for the best bid on the BTC market. This way, once the bot acquires an alt coin it has a high chance of selling it all quickly. Most often, the bot cancels the order corresponding to the first trade of the sequence and starts the loop over, but it ensures that the other parts of the sequence get completed and this usually happens quickly. 

# dependencies and use

[python wrapper of the Binance API](https://github.com/sammchardy/python-binance) along with its dependencies

You need to copy and paste your binance api key and secret where it says `"copy and paste here"` at the top of the module, and have on Binance at least .1 ETH. You should also have some BNB for paying fees. There are four attributes that should be user-defined. See the comments under `if __name__ == "__main__":` for this. While running, the bot won't print anything to the screen, but it runs outside of the main thread, so you can call various methods from `BinanceArbBot` and `Client` to see what's going on. You can also change the values of the user-defined attributes, except `thread_num`, in real-time. Here's an example of my shell with the bot running:
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

ETH: 0x4da564118a8585fd6e63a7c0066d51e7a16464d5

BTC: 146qGfUuk4Ts6avXvKh1aZer2i7b7Ey21e

LTC: LZdiBF9CkrPKL5njV22bmADKuuhhm5ZTQS
