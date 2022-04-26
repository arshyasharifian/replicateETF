from alpaca_trade_api.rest import REST, TimeFrame
import alpaca_trade_api as tradeapi
from decimal import *

api = REST()
#print(api.get_bars("AAPL", TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df)
api.submit_order(symbol="PBCT", 
                    notional=1, 
                    side="buy",
                    type="market")

exit(0)

#account api
api = tradeapi.REST()
account = api.get_account()
# print(account.cash)
# print(api.list_positions())

x = 5
y = .95

y = y/100

x = x*y
print(round(x, 9))