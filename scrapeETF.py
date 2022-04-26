from cgitb import small
from math import floor
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from alpaca_trade_api.rest import REST, TimeFrame
import alpaca_trade_api as tradeapi
from decimal import *
from selenium.webdriver.support.ui import WebDriverWait       
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC

'''
brew install phantomjs
or
brew tap homebrew/cask
brew cask install chromedriver
'''
# from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

def get_etf_holdings(etf_symbol):
    '''
    etf_symbol: str
    
    return: pd.DataFrame
    '''
    url = f'https://www.barchart.com/stocks/quotes/{etf_symbol}/constituents?page=all'

    # Loads the ETF constituents page
    browser = WebDriver()
    browser.get(url)
    try:
        clickShowAllButton = WebDriverWait(browser, 2).until(EC.element_to_be_clickable((By.CLASS_NAME, 'show-all.ng-scope'))).click()
    except Exception as e:
        print(e)

    time.sleep(15)
    
    # Reads the ETF holdings table
    html = browser.page_source
    soup = BeautifulSoup(html, features="html.parser")
    # TODO - wait for table implemenet logic for clickShowAllButton
    table = soup.find('table')

    # Reads the holdings table line by line and appends each asset to a
    # dictionary along with the holdings percentage
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

def getAvailableCashValue():
    api = tradeapi.REST()
    account = api.get_account()
    availableCash = account.cash
    return int(float(availableCash))

def getMimimumDollars(etfAssetDict):
    minimumDollars = 0
    lowestPercentage = 100
    lowestEquity = 'empty'
    for key in etfAssetDict.keys():
        equity = etfAssetDict[key]
        percent = equity['percent']/100
        if percent < lowestPercentage:
            lowestEquity = equity
            lowestPercentage = percent
        minimumDollars+=floor(1/percent)
    
    #reduce the total minimum dollars to ensure smallest equity meets minimum notional requirement of $1
    smallestInvestment = minimumDollars*lowestEquity['percent']/100
    if smallestInvestment > 1:
        minimumDollars = minimumDollars/smallestInvestment
    return floor(minimumDollars)

def main():
    # get all assets under ETF
    # TODO - this should be a try-catch
    etfAssetDict = get_etf_holdings('VPC')

    #check if holdings are "fractionable"

    # identify the mimimum amount of purchasing power to build ETF
    minimumDollars = getMimimumDollars(etfAssetDict)

    # determine whether available cash enough to build ETF
    if getAvailableCashValue() < minimumDollars:
        print ("Insufficient fund to build ETF")
    else:
        investmentAmount = -1
        while investmentAmount < minimumDollars:
            investmentAmount = int(input(f"Based on the ETF, please enter a value greater than {minimumDollars} to invest: "))
        #build Alpaca client
        api = REST()
        for key in etfAssetDict.keys():
            equity = etfAssetDict[key]
            percent = equity['percent']/100
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
