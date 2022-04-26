from bs4 import BeautifulSoup
import time
from alpaca_trade_api.rest import REST
import alpaca_trade_api as tradeapi
from selenium.webdriver.support.ui import WebDriverWait       
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from math import ceil

class ETFHandler:
    def _validateETFrequest(self, requestETF):
        url = f'https://www.barchart.com/stocks/quotes/{requestETF}/constituents?page=all'

        # Loads the ETF constituents page
        browser = WebDriver()

        browser.get(url)

        time.sleep(10)

        try:
            pageNotFound = browser.find_element(By.XPATH, '//title[text()="Page not found"]')
            if pageNotFound:
                return False
                
        except Exception as e:
            print(e)
            return True

    # START of PUBLIC Function
    def getETFTable(self, etfSymbol):
        url = f'https://www.barchart.com/stocks/quotes/{etfSymbol}/constituents?page=all'

        # Loads the ETF constituents page
        browser = WebDriver()
        browser.get(url)
        try:
            WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'show-all.ng-scope'))).click()
        except Exception as e:
            print(e)
            exit(0)

        time.sleep(3)
        
        # Reads the ETF holdings table
        html = browser.page_source
        soup = BeautifulSoup(html, features="html.parser")
        table = soup.find('table')

        # Reads the holdings table line by line and appends each asset to a dictionary along with the holdings percentage
        asset_dict = {}
        for row in table.select('tr')[1:-1]:
            try:
                cells = row.select('td')
                # print(row)
                symbol = cells[0].get_text().strip()
                #print(symbol)
                name = cells[1].text.strip()
                celltext = cells[2].get_text().strip()
                percent = float(celltext.rstrip('%'))
                if symbol != "" and percent != 0.0:
                    asset_dict[symbol] = {
                        'name': name,
                        'percent': percent,
                }
            except BaseException as ex:
                print(ex)
        browser.quit()
        return asset_dict
        
    def getAvailableCash(self):
        api = tradeapi.REST()
        account = api.get_account()
        availableCash = account.cash
        return int(float(availableCash))

    def getMimimumDollars(self, etfSymbol):
        # calls get_etf_holdings, must pass in ETF symbol

        etfAssetDict = self.getETFTable(etfSymbol)
        
        minimumDollars = 0
        lowestPercentage = 100
        lowestEquity = 'empty'
        for key in etfAssetDict.keys():
            equity = etfAssetDict[key]
            percent = equity['percent']/100
            if percent < lowestPercentage:
                lowestEquity = equity
                lowestPercentage = percent
            minimumDollars+=ceil(1/percent)
        
        #reduce the total minimum dollars to ensure smallest equity meets minimum notional requirement of $1
        smallestInvestment = minimumDollars*lowestEquity['percent']/100
        if smallestInvestment > 1:
            minimumDollars /= smallestInvestment
        return ceil(minimumDollars)

    def rebalance():
        '''
        take the current porfolio
        determine what is inconsistent with the ETF
        makes adjustment to sync with ETF changes
        '''


def main():

    myETFHandler = ETFHandler()

    symbol = "VOO"
    etfAssetDict = myETFHandler.getETFTable(symbol)

    #check if holdings are "fractionable"

    # identify the mimimum amount of purchasing power to build ETF
    minimumDollars = myETFHandler.getMimimumDollars(symbol)

    # determine whether available cash enough to build ETF
    if myETFHandler.getAvailableCash() < minimumDollars:
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

if __name__ == "__main__":
    main()
