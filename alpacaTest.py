from alpaca_trade_api.rest import REST, TimeFrame
api = REST()
print(api.get_bars("AAPL", TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df)