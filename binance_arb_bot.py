__author__ = 'Nathan Ezra Schmidt'
__email__ = 'nathanezraschmidt@gmail.com'

import time
import math
import threading
from binance.client import Client
from binance.websockets import BinanceSocketManager

api_key = "copy and past here"
api_secret = "copy and paste here"

def floor(n, r):
    """
    n is float, r is int, returns string
    rounds n down to r decimal places, and converts result to string while avoiding scientific notation
    used for the price param in placing orders
    example:
    >>> floor(.000000065423, 11)
    '0.00000006542'
    """
    if r <= 0:
        return str(int(n))
    s = str(float(n))
    if 'e' in s:
        s1 = s.split('e-')
        s2 = ''
        for i in range(int(s1[1]) - 1):
            if i == '.':
                continue
            s2 = s2 + '0'
        s3 = ''
        for i in  s1[0]:
            if i == '.':
                continue
            s3 = s3 + i
        s = '0.' + s2 + s3
        return s[:r+2]
    else:
        s = s.split('.')
        return s[0] + '.' + s[1][:r]

def ceil(n, r):
    """
    same as floor, but rounds up
    """
    if r <= 0:
        return str(int(n) + (float(n) > int(n)))
    s = str(float(n))
    if 'e' in s:
        s1 = s.split('e-')
        s2 = ''
        for i in range(int(s1[1]) - 1):
            if i == '.':
                continue
            s2 = s2 + '0'
        s3 = ''
        for i in s1[0]:
            if i == '.':
                continue
            s3 = s3 + i
        s = '0.' + s2 + s3
        if len(s) > r + 2:
            return s[:r+1] + str(int(s[r+1])+1)
        else:
            return s[:r+2]
    else:
        s = s.split('.')
        x = s[1]
        if len(s[1]) > r:
            x = s[1][:r-1] + str(int(x[r-1])+1)
        return s[0] + '.' + x[:r]

class BinanceArbBot:
    def __init__(self, client, starting_amount, expected_roi, wait_time):
        self.client, self.starting_amount, self.min_ev, self.wait_time = \
        client, starting_amount, expected_roi + 1, wait_time
        self.c1 = 'ETH'
        self.c2 = 'BTC'
        self.btc_min_balance = .0012

        # put exchange info into dict where values are symbols, for easy access and placing orders without error
        
        info = self.client.get_exchange_info()
        self.quantity_round, self.min_quantity, self.max_quantity,self. min_notional, self.tick_size, self.price_round = {}, {}, {}, {}, {}, {}

        for s in info['symbols']:        
            symbol = s['symbol']
            stepSize = s['filters'][1]['stepSize']
            self.quantity_round[symbol] = stepSize.index('1') - 1
            self.min_quantity[symbol] = s['filters'][1]['minQty']
            self.max_quantity[symbol] = s['filters'][1]['maxQty']
            self.min_notional[symbol] = s['filters'][2]['minNotional']
            self.tick_size[symbol] = float(s['filters'][0]['tickSize'])
            self.price_round[symbol] = s['filters'][0]['tickSize'].index('1') - 1

        symbols = self.price_round.keys()
        self.price_round_float = {}

        for i in self.price_round.keys():
            self.price_round_float[i] = 1/math.pow(10, self.price_round[i])
        self.alts = []
        
        # self.alts = alts (base currencies) common to both ETH and BTC markets
        
        for s in symbols:
            if s.endswith("ETH"):
                if s[:-3] + "BTC" in symbols:
                    self.alts.append(s[:-3])
                    
        self.alts.remove("BNB")
        self.occupied_alts = {}
        
        for alt in self.alts: 
            self.occupied_alts[alt] = 0

        self.orderbook_tickers_dict, self.order_info_dict, self.trade_status_dict  = {}, {}, {}
        
        for alt in self.alts + ['BNB']: # initialized self.trade_status_dict
            self.trade_status_dict[alt+'ETH'] = {'s':alt+'ETH', 'x':'NEW', 'q':'0', 'X':'NEW'}
            self.trade_status_dict[alt+'BTC'] = {'s':alt+'BTC', 'x':'NEW', 'q':'0', 'X':'NEW'}
        self.trade_status_dict['ETHBTC'] = {'s':'ETHBTC', 'x':'NEW', 'q':'0', 'X':'NEW', 'T':0}
        self.trade_status_dict['ETHUSDT'] = {'s':'ETHUSDT', 'x':'NEW', 'q':'0', 'X':'NEW', 'T':0}
        self.trade_status_dict['XLMBNB'] = {'s':'XLMBNB', 'x':'NEW', 'q':'0', 'X':'NEW', 'T':0}
        
        self.sell_price_dict, self.asset_balances = {}, {}

        self.pivot_lock = threading.Lock()
        self.buy_eth_lock = threading.Lock()

        self.orderbook_tickers = self.client.get_orderbook_tickers()
        self.orderbook_tickers_dict = {}
        for i in self.orderbook_tickers: # initialize values of self.orderbook_tickers_dict
            self.orderbook_tickers_dict[symbol] = i['symbol']
        
    def init_asset_balances(self, starting_amount=.02, symbol='XLMETH'):
        """
        places buy order that doesn't fill, and then cancels, to get websocket response that gives sends balances of all assets
        account needs to have at least as much ETH as the value for starting_amount
        """
        symbol = symbol.upper()
        self.place_buy_order(symbol, starting_amount=starting_amount, price=self.get_bid_ask(symbol)[0]/2)
        self.client.cancel_order(symbol=symbol, orderId=self.order_info_dict[symbol]['orderId'])
        
    def get_bid_ask(self, symbol):
        symbol = symbol.upper()
        try: # faster, using websocket
            x = (self.orderbook_tickers_dict[symbol])
            return float(x['b']), float(x['a'])
        except: # slower, using rest if websocket connection hasn't been established
            b = self.client.get_ticker(symbol=symbol)
            return float(b['bidPrice']), float(b['askPrice'])
                    
    def get_asset_balance(self, symbol):
        symbol = symbol.upper()
        try: # faster, using websocket
            return float(self.asset_balances[symbol]['f']) + float(self.asset_balances[symbol]['l'])
        except KeyError: # slower, using rest if websocket connection hasn't been established
            x = self.client.get_asset_balance(asset = symbol)
            return float(x['free']) + float(x['locked'])

    def get_pivot(self):
        
        """
        pivot is an alt coin that is traded on both ETH and BTC markets
        for each pivot, an ev is computed from the following three part trade sequence: buy pivot with ETH at current best bid price, sell pivot to BTC at current best bid price, buy ETH with BTC at current best ask price
        returns, as a string, the name of whichever pivot currently not being used in any open orders returns the highest ev when used as part of the above sequence, if that ev is at least as high as self.min_ev, otherwise returns False 
        if returns pivot, sets self.occupied_alts[pivot] to 1
        """
        with self.pivot_lock:
            try:
                bid = float(self.orderbook_tickers_dict[self.c1+self.c2]['b'])
                ask = float(self.orderbook_tickers_dict[self.c1+self.c2]['a'])
            except:
                bid = float(self.orderbook_tickers_dict[self.c2+self.c1]['b'])
                ask = float(self.orderbook_tickers_dict[self.c2+self.c1]['a'])
            pivot, best_ev = False, 0
            for alt in self.alts:
                if self.occupied_alts[alt]:
                    continue
                try:
                    s1, s2 = alt + self.c1, alt + self.c2
                    t1, t2 = self.orderbook_tickers_dict[s1], self.orderbook_tickers_dict[s2]
                    bid_1, bid_2 = float(t1['b']), float(t2['b'])
                except:
                    continue
                if self.c1 == "ETH":
                    ev = (bid_2/bid_1)/ask
                else:
                    ev = (bid_2/bid_1)*bid
                if ev > best_ev:
                    best_ev = ev
                    pivot = alt
                    self.sell_price_dict[alt] = bid_2
            if best_ev >= self.min_ev:
                self.occupied_alts[pivot] = 1
                return pivot
            else:
                return False

    def quantity_errors_buy(self, qty, symbol, bid):
        """
        used to check if buy amount of base currency will result in error
        """
        if qty < float(self.min_quantity[symbol]):
            return 'buy quantity too low'
        elif qty > float(self.max_quantity[symbol]):
            return 'buy quantity too high'
        if qty*float(bid) < float(self.min_notional[symbol]):
            return 'purchase too small'
        return False

    def quantity_errors_sell(self, qty, symbol, price):
        """
        used to check if sell amount of base currecny will result in error
        """
        if qty < float(self.min_quantity[symbol]): # base coin amount
            return 'not enough to sell'
        if qty*price < float(self.min_notional[symbol]): # quote coin amount
            return 'sale too small'
            print(self.min_notional[symbol], qty*price)
        return False
                
    def place_buy_order(self, s='ethbtc', starting_amount=1, price=0, qty=0):
        """
        s is symbol
        starting_amount is amount of quote coin (ETH or BTC)
        if price is 0, then places order at highest bid
        qty is quantity of quote coin to buy. if 0, then price and starting_amount are used to calculate it
        called from self.buy_pivot or command len, if the former and returns 'error', self.buy_pivot returns as if order had been canceled
        """
        s = s.upper()
        if price == 0:
            bid = self.get_bid_ask(s)[0]
            bid = floor(bid, self.price_round[s])
        else:
            bid = floor(price, self.price_round[s])
        if qty == 0:
            qty = starting_amount/float(bid) # qty is of coin being bought
        qty = float(floor(qty, self.quantity_round[s]))

        if self.quantity_errors_buy(qty, s, bid):
            return 'error'
        try:
            self.order_info_dict[s] = self.client.order_limit_buy(timeInForce='GTC', symbol=s, price= bid, quantity=qty)
            return None
        except:
            return 'error'

    def place_sell_order(self, s='ethbtc', starting_amount=0, price=0):
        """
        starting_amount is amount of base coin to sell. If 0, then sells all.
        if price is 0, then sells at best ask
        called from self.sell_pivot or command line, if the former and returns 'error', self.sell_pivot returns as if order had been filled (will often return 'error' after a successful sale due to insufficient balance)
        """
        s = s.upper()
        if price == 0:
            ask = self.get_bid_ask(s)[1]
            ask = ceil(ask, price_round[s])
        else:
            ask = ceil(price, self.price_round[s])
        alt = s[:-3]
        if s == 'ETHUSDT':
            alt = 'ETH'
        max_sell = float(self.get_asset_balance(alt))
        if starting_amount:
            max_sell = min(max_sell, starting_amount)
        if max_sell == 0:
            return 'error'
        qty = float(floor(max_sell, self.quantity_round[s]))
        if self.quantity_errors_sell(qty, s, float(ask)):
            return 'error'
        try:
            self.order_info_dict[s] = self.client.order_limit_sell(timeInForce='GTC', symbol=s, price=ask, quantity=qty)
            return None
        except:
            text = 'sell args = ' + s + ' ' + str(ask) + ' '  + str(qty)
            with print_lock:
                print('unknown sell error', text)
                print(self.trade_status_dict[s])
        return 'error'
        
    def cancel_order(self, symbol):
        try:
            self.client.cancel_order(symbol=symbol, orderId=self.order_info_dict[symbol]['orderId'])
        except:
            pass

    def cancel_all_orders(self):
        for order in self.client.get_open_orders():
            self.client.cancel_order(symbol=order['symbol'], orderId=order['orderId'])

    def buy_pivot(self):
        """
        places order at current bid price to buy pivot coin.
        holds or renews order until price on either ETH or BTC market has changed such that expected ROI is less than self.roi,
        at which point it cancels
        should return only when order has been partially, or totally filled or canceled. 
        if for whatever reason (most commonly account getting temporarily disabled by binance), returns without doing either
        and order is left hanging, it will get canceled by self.clean_up_buys if called periodically in its own thread
        """
        pivot = False
        while not pivot:
            pivot = self.get_pivot()
        symbol = pivot + self.c1
        buy_price = self.get_bid_ask(symbol)[0]
        sell_price = self.sell_price_dict[pivot] 
        qty = float(self.orderbook_tickers_dict[pivot + self.c2]['B'])
        starting_amount = min(self.starting_amount, float(self.asset_balances[self.c1]['f']))
        qty = min(qty, starting_amount/buy_price)
        x = self.place_buy_order(symbol, self.starting_amount, buy_price, qty)
        if x == 'error':
            return pivot
        while True:
            if buy_price < self.get_bid_ask(symbol)[0]: 
                break
            if sell_price > self.get_bid_ask(pivot+self.c2)[0]:
                break
            if self.trade_status_dict[symbol]['x'] == 'TRADE':
                break
        self.cancel_order(symbol)
        return pivot

    def sell_pivot(self, pivot, sell_at_ask=False, sell_to_eth=False):
        """
        places sell order first at price used in calculated roi, which should be at the bid
        will return until order is filled or account has less than min quantity required to make a sale
        after first order, will renew when needed to keep the best asking price position
        """
        symbol = pivot + self.c2
        if sell_to_eth:
            symbol = pivot + "ETH"
        try:
            sell_price = self.sell_price_dict[pivot]
        except:
            sell_price = self.get_bid_ask(symbol)[0]
        if sell_at_ask:
            sell_price = self.get_bid_ask(symbol)[1]
        while True:
            x = self.place_sell_order(symbol, starting_amount=0, price=sell_price)
            if x == 'error':
                break
            while sell_price <= self.get_bid_ask(symbol)[1]:
                if self.trade_status_dict[symbol]['X'] == 'FILLED':
                    break
            sell_price = self.get_bid_ask(symbol)[1]
            self.cancel_order(symbol)
        self.occupied_alts[pivot] = 0
            
    def make_trades(self):
        """
        starts trading, called once per thread
        """
        while True:
            self.sell_pivot(self.buy_pivot())
            time.sleep(self.wait_time)
   
    def buy_eth(self):
        """
        detects when account has acquired BTC and uses it to buy ETH at the bid price
        returns when account has less BTC than self.btc_min_balance
        """
        with self.buy_eth_lock:
            symbol = 'ETHBTC'
            while self.get_asset_balance("BTC") >= self.btc_min_balance:
                price = self.get_bid_ask(symbol)[0]
                x = self.place_buy_order(symbol, self.get_asset_balance("BTC"), price)
                if x == 'error':
                    self.cancel_order(symbol)
                    return
                while price >= self.get_bid_ask(symbol)[0] and self.trade_status_dict[symbol]['X'] != 'FILLED':
                    pass
                self.cancel_order(symbol)
            return
        
    def buy_eth_loop(self):
        while True:
            self.buy_eth()
                
    def clean_up_alts(self):
        """
        in case alt is bought without bot knowing, will sell it at best ask
        similar to self.clean_up_buys
        if account is temporarily disabled or disconnected, a buy order may accidentally get filled (happens rarely)
        """
        while True:
            for alt in self.alts: # all alts
                balance = float(self.asset_balances[alt]['f'])
                if balance*self.get_bid_ask(alt+'BTC')[0] >= .00012:
                    threading.Thread(target=self.sell_pivot, args=(alt, True)).start()
            time.sleep(600)

    def clean_up_eth(self, alt):
        balance = self.get_asset_balance(alt)
        t = threading.Thread(target=self.sell_pivot, args=(alt, True, True))
        t.start()

    def clean_up_buys(self):
        """
        called every 600 seconds to cancel buy orders that because of UB or error haven't been properly canceled
        (rarely needed)
        """
        while True:
            time.sleep(600)
            try:
                orders = self.client.get_open_orders()
            except:
                time.sleep(10)
                try:
                    orders = self.client.get_open_orders()
                except:
                    return
            current_time = time.time()
            min_elapsed_time = 60
            for order in orders:
                if (current_time - order['time']/1000  < min_elapsed_time or order['side'] == 'SELL') and order['status'] == 'NEW':
                    continue
                price = float(order['price'])
                symbol = order['symbol']
                if self.get_bid_ask(symbol)[0] != price or order['status'] != 'NEW':
                    try:
                        self.client.cancel_order(symbol=symbol, orderId=order['orderId'])
                    except:
                        pass

    def show_alt_balances(self):
        y = [(alt, self.get_asset_balance(alt)) for alt in self.alts]
        y = [(i[0], i[1]*self.get_bid_ask(i[0]+'ETH')[0]) for i in y if i[1]]
        return sorted(y, key=lambda f:f[1], reverse=True)

    def show_eth_total(self, alts):
        x = self.get_asset_balance('ETH')
        for alt in alts:
            x += self.get_asset_balance(alt.upper())*self.get_bid_ask(alt.upper()+'ETH')[0]
        return x

    def show_eth_value(self):
        """
        ETH value of all alts and USDT, except BNB
        """
        return self.show_eth_total(self.alts) + self.get_asset_balance("USDT")/self.get_bid_ask("ETHUSDT")[0]

    def show_value_info(self):
        print(self.show_eth_value())
        print(self.get_asset_balance("ETH"))
        print(self.get_asset_balance("BNB"))
        print(self.get_asset_balance("BTC"))
        print(self.get_bid_ask('ETHUSDT'))

    def get_time_diff(self):
        return  self.client.get_server_time()['serverTime']-int(time.time()*1000)

    def test_time(self):
        """
        if asbolute value of diff is more than 1000, sync computer time
        """
        print('server time - client time =', self.get_time_diff())
            
if __name__ == "__main__":
    
    client = Client(api_key, api_secret, {'timeout':600})

    # Important: values for the following four variables should be set by user (somewhat account / user dependent), everything else shouldn't be altered

    thread_num = 4 # number of trades to make simultaneously
    starting_amount = .2 # max quantity of ETH to be used per trade
    expected_roi = .0028 # expected roi for each trading sequence before fees, assuming buys and sells are made at predicted prices, should be between .0025 and .004
                         # lower values result in more trades, but lower ev per trade
                        
    wait_time = 2 # number of seconds to wait after trading sequence finishes, used to minimize account getting temporarily disabled
                    # if more than 4 threads (i.e., thread_num >= 4) should increase by 2 or 3 for each additional thread

    bab = BinanceArbBot(client, starting_amount=starting_amount, expected_roi=expected_roi, wait_time=wait_time)

    def update_orderbook_dict(msg): # callback function for start_ticker_socket
        for d in msg:
            bab.orderbook_tickers_dict[d['s']] = d

    def update_user(msg): # callback function for start_user_socket
        if msg['e'] == 'executionReport':
            bab.trade_status_dict[msg['s']] = msg
        else:
            balances = msg['B']
            for i in balances:
                bab.asset_balances[i['a']] = i
            if (not bab.buy_eth_lock.locked() and bab.c1 == 'ETH' and float(bab.asset_balances['BTC']['f']) + float(bab.asset_balances['BTC']['l'])) >= bab.btc_min_balance:
                threading.Thread(target=bab.buy_eth).start()

    bm = BinanceSocketManager(client)

    bm.start_ticker_socket(update_orderbook_dict)
    bm.start_user_socket(update_user)

    bm.start()
    time.sleep(2) # wait for websocket response

    bab.init_asset_balances()

    while not 'QTUM' in bab.asset_balances: # wait for websocket response to get all asset balances, QTUM is normally one of last assets to get
        pass

    threading.Thread(target=bab.clean_up_buys).start() # start thread to clean up buy orders
    threading.Thread(target=bab.clean_up_alts).start() # start thread to clean sell alts in case of having failed to sell
    
    def start_trading(thread_num):
        for i in range(thread_num):
            threading.Thread(target=bab.make_trades).start()

    start_trading(thread_num) # start running bot
    
