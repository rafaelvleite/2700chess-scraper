import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import undetected_chromedriver as uc
from retry import retry

def openBrowser():

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument( '--headless' )
    driver = uc.Chrome(options=options)
    
    return driver 

@retry(delay=2, tries=6)
def setPage(driver, rating):
    driver.get("https://2700chess.com/all-fide-players")
    el1 = WebDriverWait(driver, 16).until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@id="ratingFromFilter"]')))
    el1.clear()
    el1.send_keys(rating)

    el2 = WebDriverWait(driver, 16).until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@id="ratingToFilter"]')))
    el2.clear()
    el2.send_keys(rating)
    
    s = Select(driver.find_element("xpath", "//select[@id='count']"))
    s.select_by_value('100')

    buttonToClick = driver.find_element(by=By.CLASS_NAME, value="btn-2700")
    buttonToClick.click()
    return True

@retry(delay=2, tries=6)
def getHtml(driver):
    html=driver.execute_script('return document.getElementById("official-ratings-table").innerHTML')
    parsed_html = BeautifulSoup(html,'lxml') #scrape data
    return parsed_html

def dataframeFromPage(parsed_html):
    tableBody = parsed_html.find('tbody', attrs={"class":"list"})
    tableRows = tableBody.find_all('tr')
    
    index = 0
    playersDict = {}
    for row in tableRows:
        dataList = row.text.replace(" ", "").split("\n")
        playersDict[index] = dataList
        index += 1
    if playersDict[0][1] != "NoResultsFound!":
        localDf = pd.DataFrame.from_dict(playersDict, columns=\
            ['Empty', 'Empty', 'Empty', 'Empty', 'Title', 'Empty', 'Empty', 'Name', 'Empty', 'Empty', 'Empty', \
            'Country', 'Empty', 'Empty', 'Empty', 'Empty', 'Classic', 'Empty', 'Empty', 'Empty', \
            'Rapid', 'Empty', 'Empty', 'Empty', 'Blitz', 'Empty', 'Empty', 'Age', 'Empty'], orient='index')
        del localDf['Empty']
    else:
        localDf = pd.DataFrame()

    return localDf


if __name__ == "__main__":
    
    ratingRange = range(2300, 2900)
    
    driver = openBrowser()
    
    finalDf = pd.DataFrame()
    incompleteRatings = []
    for rating in ratingRange:
        print(rating)
        setPage(driver, rating)
        time.sleep(2)
        parsed_html = getHtml(driver)
        localDf = dataframeFromPage(parsed_html)
        if len(localDf) >=100:
            incompleteRatings.append(rating)
            print("Incomplete for {}".format(rating))
        concat = [finalDf, localDf]
        finalDf = pd.concat(concat)
    
    finalDf.sort_values(by=['Classic'], inplace=True)
    finalDf.reset_index(drop=True, inplace=True)
    finalDf.to_csv('2700_data.csv', index=False)
    driver.quit()
        
