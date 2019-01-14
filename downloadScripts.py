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
# Import smtplib for the actual sending function
import smtplib

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

    def scroll_to_and_click(self, driver, xpath):
        element = driver.find_element_by_xpath(xpath)
        driver.execute_script('window.scrollTo(' + str(element.location['x']) + ', ' + str(element.location['y']) + ');')
        element.click()

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
            #chrome_options.add_argument("screenshot")
            driver = webdriver.Chrome(driver_location, chrome_options=chrome_options)


        for app in self.__apps:                        
            print ("Checking " + app[0] + "...")        
            #try:
            driver.implicitly_wait(10)        
            driver.get(app[1])

            # # Perform the login
            driver.find_element_by_xpath(app[2]).send_keys(self.__user)
            driver.find_element_by_xpath(app[3]).send_keys(self.__pwd)
            driver.find_element_by_xpath(app[4]).click()    

            # Get to the Scripts Section
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[6]))).click()
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[7]))).click()
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[8]))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="header-menu-toggle"]'))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="configuration"]'))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="configuration-scripts"]'))).click()

            # Show all Scripts            
            showElements = driver.find_element_by_xpath('//*[@id="pager"]/li[1]/div/select') 
            # showElements = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pager"]/li[1]/div/select'))); 
            sel = Select(showElements)
            #sel.select_by_visible_text("All items per page")
            sel.select_by_value("770")
            #time.sleep(10)

            # Select table 
            count_all_trs = len(driver.find_elements_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"]'))
            for tr in range(count_all_trs-1):                        
                elem = driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span')
                try:
                    elem.click()
                except:
                    # print "failed to click"
                    size = elem.size
                    mid_of_y = int(size["height"])/2
                    stepts_to_do_to_left = int(size["width"])
                    while stepts_to_do_to_left > 0:
                        try:
                            #print stepts_to_do_to_left, mid_of_y
                            action = webdriver.common.action_chains.ActionChains(driver)
                            action.move_to_element_with_offset(elem, mid_of_y, stepts_to_do_to_left)
                            action.click()
                            action.perform()
                            #print "DONE CLICK"
                            break
                        except:
                            pass

                try:            
                    #driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span').click()
                    driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]/span/a').click()
                    driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]//ul[@class="bmc-actioncolumn"]/li[3]/a').click()
                    driver.find_element_by_xpath('/html/body/article/div/section/div[2]/table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span').click()
                    print("download num " + str(tr))
                except:
                    pass

                if tr > 20:
                    break

            # driver.find_element_by_xpath('//*[@id="pager"]/li[3]/ul/li[4]/a').click()     
            
            # Logoff
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="user-preferences-header-action-menu"]'))).click()            
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="logout-header-opition"]'))).click()
            time.sleep(15)

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

screenshotPath = '\\\\personal\\personal$\\CORTEAG\\repo\\truesight\\screenshots\\'
xmlPath = '\\\\personal\\personal$\\CORTEAG\\repo\\truesight\\status\\' #'/home/opsmon/scripts/dashboard/health/'
xmlFile = 'core_status.html'

ff = downloadScripts(apps, screenshotPath , xmlPath , xmlFile , True)
ff.proceedDownload()
