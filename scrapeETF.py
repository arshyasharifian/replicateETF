import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
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

    # Loads the ETF constituents page and reads the holdings table
    browser = WebDriver() # webdriver.PhantomJS()
    browser.get(url)
    browser.maximize_window()
    time.sleep(40)
    # button = browser.find_element(by=By.CLASS_NAME, value='show-all ng-scope')
    content = browser.find_element_by_class_name("show-all.ng-scope")

    content.click()
    time.sleep(40)
    html = browser.page_source
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find('table')

    # Reads the holdings table line by line and appends each asset to a
    # dictionary along with the holdings percentage
    asset_dict = {}
    for row in table.select('tr')[1:-1]:
        try:
            cells = row.select('td')
            # print(row)
            symbol = cells[0].get_text().strip()
            print(symbol)
            name = cells[1].text.strip()
            celltext = cells[2].get_text().strip()
            percent = float(celltext.rstrip('%'))
            # shares = int(cells[3].text.strip().replace(',', ''))
            if symbol != "" and percent != 0.0:
                asset_dict[symbol] = {
                    'name': name,
                    'percent': percent,
                    # 'shares': shares,
                }
        except BaseException as ex:
            print(ex)
    browser.quit()
    return pd.DataFrame(asset_dict)


myf = get_etf_holdings('VOO')
pd.DataFrame(myf).to_csv('test.csv')
print(myf)