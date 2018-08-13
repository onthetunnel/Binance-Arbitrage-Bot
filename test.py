from binance_arb_bot import *
api_key = "copy and paste here"
api_secret = "copy and paste here"

client = Client(api_key, api_secret, {'timeout':600})

eth_balance = client.get_asset_balance(asset='ETH')
bnb_balance = client.get_asset_balance(asset='BNB')

if float(eth_balance['free']) < .1:
    print('\nETH balance too low!')
    print('eth balance =', eth_balance)
    raise Exception("ETH balance too low")

if float(bnb_balance['free']) < .5:
    print('\nBNB balance too low!')
    print('bnb balance =', bnb_balance)
    raise Exception("BNB balance too low")

bab = BinanceArbBot(client, starting_amount=0, expected_roi=0, wait_time=0)

bab.test_time()

if abs(bab.get_time_diff()) > 1000:
    print('sync computer time within 1000 millisecond of server time')
    raise Exception("computer time not synced with server time")

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

print('open orders =', client.get_open_orders())
print('\nplacing buy order\'t get filled\n') #this order won't get filled due to low price
bab.place_buy_order('XLMETH', starting_amount=.1, price=bab.get_bid_ask('XLMETH')[0]/2)
print('\nopen orders =', client.get_open_orders())
print('\ncanceling order\n')

symbol = 'XLMETH'

bab.client.cancel_order(symbol=symbol, orderId=bab.order_info_dict[symbol]['orderId'])
print('\nopen orders =', client.get_open_orders())

