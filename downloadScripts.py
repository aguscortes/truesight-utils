from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time, os


# Import the email modules we'll need
from email.mime.text import MIMEText

class downloadScripts():

     # Locations        
    __screenshotPath = ''
    __xmlPath = ''

    # File Names
    __xmlFile = ''

    # Apps List
    __apps = []
    __results = []

    # Parameters related to brownser
    __visible = False

    # Credentials
    __user = ''
    __pwd = ''

    def __init__ (self, apps, screenshotPath, xmlPath, xmlFile, visible):
        self.__apps = apps
        self.__screenshotPath = screenshotPath
        self.__visible = visible
        self.__xmlPath = xmlPath 
        self.__xmlFile = xmlFile 


    def proceedDownload(self):     
        self.__results = []
        successReached = False
        successLogged = False

        driver_location = os.path.join('D:','lib','chromedriver.exe')
        os.environ["webdriver.chrome.driver"] = driver_location
        if self.__visible:
            driver = webdriver.Chrome(driver_location)
        else:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(driver_location, chrome_options=chrome_options)


        for app in self.__apps:                        
            print ("Checking " + app[0] + "...")        
            driver.implicitly_wait(10)        
            driver.get(app[1])

            # Perform the login
            driver.find_element_by_xpath(app[2]).send_keys(self.__user)
            driver.find_element_by_xpath(app[3]).send_keys(self.__pwd)
            driver.find_element_by_xpath(app[4]).click()    

            # Get to the Scripts Section
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="header-menu-toggle"]'))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="configuration"]'))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="configuration-scripts"]'))).click()

            # Show all Scripts            
            showElements = driver.find_element_by_xpath('//*[@id="pager"]/li[1]/div/select') 
            sel = Select(showElements)
            sel.select_by_value("770")
           
            # Select table 
            count_all_trs = len(driver.find_elements_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"]'))
            for tr in range(count_all_trs-1):                        
                elem = driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span')
                try:
                    elem.click()
                except:
                    size = elem.size
                    mid_of_y = int(size["height"])/2
                    stepts_to_do_to_left = int(size["width"])
                    while stepts_to_do_to_left > 0:
                        try:
                            action = webdriver.common.action_chains.ActionChains(driver)
                            action.move_to_element_with_offset(elem, mid_of_y, stepts_to_do_to_left)
                            action.click()
                            action.perform()
                            break
                        except:
                            pass

                driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]/span/a').click()
                driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]//ul[@class="bmc-actioncolumn"]/li[3]/a').click()
                driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span').click()
                print("download num " + str(tr))
            
            # Logoff
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="user-preferences-header-action-menu"]'))).click()            
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="logout-header-opition"]'))).click()

        driver.quit()
        return self.__results

apps = [('Truesight', 'https://truesightps.prod.oami.eu:8043/#/', 
            '//input[@placeholder="User Name"]', '//input[@placeholder="Password"]', '//button[@type="submit"]', 
            '//*[@id="logout-header-opition"]',
            '//*[@id="configuration"]',            
            '//a[@id="header-menu-toggle"]',
            '//a[@id="configuration"]',
            '//a[@id="configuration-scripts"]',
            True, False, '//map[@name="Map"]/area[contains(@href, "logout")]')]

screenshotPath = ''
xmlPath = '' 
xmlFile = ''

ff = downloadScripts(apps, screenshotPath , xmlPath , xmlFile , True)
ff.proceedDownload()
