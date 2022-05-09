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
    def __init__(self, api_key=None, api_secret=None, base_url='https://paper-api.alpaca.markets'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
    
    # private function 
    def _validateETFrequest(self, requestETF: str):
        """
        Checks whether the ETF symbol represents a valid page url by visiting the page
        and returning true if valid URL and false otherwise. Fail is returned when a page
        not found is parsed in the destination URL.
        """
        url = f'https://www.barchart.com/stocks/quotes/{requestETF}/constituents?page=all'
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

    def getETFTable(self, etfSymbol: str):
        """
        given the etfSymbol value, we open a chrome browser and search for the page
        if found, we expand the page to include all the equities. Finally, we construct
        a dictionary where the the key is the stock ticker and the values consist of
        1, the formal stock name and 2, what percentage the equity consist of in the ETF
        portfolio
        """
        url = f'https://www.barchart.com/stocks/quotes/{etfSymbol}/constituents?page=all'
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
        # Reads the holdings table line by line and appends each stock to a dictionary along with the holdings percentage
        asset_dict = {}
        for row in table.select('tr')[1:-1]:
            try:
                cells = row.select('td')
                # print(row)
                symbol = cells[0].get_text().strip()
                # print(symbol)
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
        """
        Based on the credentials read through environment variables, we assess the available "cash" in the account.
        A paper account is also applicable here. In other words, this can be used for testing and does not
        require actual cash. This is important to determine whether orders can be placed.
        """
        api = tradeapi.REST()
        account = api.get_account()
        availableCash = account.cash
        return int(float(availableCash))

    def getMimimumDollars(self, etfSymbol: str):
        # calls get_etf_holdings, must pass in ETF symbol
        """
        given the ETF symbol, this determine the minimum amount of dollars to satisfy the Alpaca API
        requirements for trading stocks, at least $1 of each stock must be purchased. By dividing 1 by
        the stocks's percentage we calculate the number of dollars needed to buy at least $1 dollar
        of each stock. We sum this value to calculate the total amount of dollars needed. Finally,
        we divide the sum by the smallest dollars allocated to a particular stock. This ensures we 
        will meet the minimum requirements by Alpaca.
        """

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

        """
        TODO - create a new function to rebalance portfolio based on ETF changes
        def rebalance():
            determine the differences between the user's current portfoilio and current ETF holdings.
            Buy and sell shares of the user's current portfolio to ensure there are no differences.
        """