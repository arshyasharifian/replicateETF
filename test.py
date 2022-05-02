from replicateETF.scrapeETF import ETFHandler
from alpaca_trade_api.rest import REST

myObj = ETFHandler()
symbol = "VOO"
etfAssetDict = myObj.getETFTable(symbol)

# identify the mimimum amount of purchasing power to build ETF
minimumDollars = myObj.getMimimumDollars(symbol)

# determine whether available cash enough to build ETF
if myObj.getAvailableCash() < minimumDollars:
    print ("Insufficient fund to build ETF")
else:
    investmentAmount = -1
    while investmentAmount < minimumDollars:
        investmentAmount = float(input(f"Based on the ETF, please enter a value greater than {minimumDollars} to invest: "))
    #build Alpaca client
    api = REST()
    for key in etfAssetDict.keys():
        equity = etfAssetDict[key]
        percent = equity['percent']/100
        # TODO - should be a separate function to enable retry logic
        try:
            orderResponse=api.submit_order(symbol=key, 
                            notional=investmentAmount*percent, 
                            side="buy",
                            type="market")
            print(orderResponse)
        except Exception as e:
            print(e)