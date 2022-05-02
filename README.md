# ReplicateETF

## Disclaimer:
There can be significant tax, financial, and legal consequences related to this repository and its use.
Signficant losses can occur. Trading equities is always dangerous and should be approached with extreme caution.
By using this repository, you accept all liability or consequences related to the code provided here.

## Context:
This repository allows users to purchase the underlying stocks of an ETF.

This repository uses Alpaca API, but the code can be reused for other trading platform like IEX. To directly
use the package defined here, please setup an Alpaca API [account](https://alpaca.markets/docs/).

## Export Alpaca API Keys and Base URL

This example showcases exporting the basic API keys needed to execute some of the available functions. The `BASE_URL` defined below corresponds to the paper trading for testing algorithms. There is an alternative `BASE_URL` for live trading.

Example:
```
export APCA_API_KEY_ID=<api key>
export APCA_API_SECRET_KEY=<secret key>
export APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

[Here](https://alpaca.markets/deprecated/docs/api-documentation/how-to/) is some more documentation from Alpaca on how to setup API Keys.

## Download the Package:
```
pip install -i https://test.pypi.org/simple/ replicateETF
```

## Import package:
```
from replicateETF.scrapeETF import ETFHandler
```

## Example use:
```
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
```

This example case is listed as `test.py` in the repository.

Install dependencies (these should automatically be download but just in case):
- beautifulsoup4>=4.11.1
- alpaca-trade-api>=2.0.0
- selenium>=4.1.3
