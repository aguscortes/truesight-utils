from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import time
import os
import zipfile

class itsm_scripts_management():
    # Credentials
    __token = ''
    __username = ''
    __password = ''

    __null = None
    __download_path = ''
    __xpaths =  [('Truesight', 'https://truesightps.prod.oami.eu:8043/#/', 
            '//input[@placeholder="User Name"]', '//input[@placeholder="Password"]', '//button[@type="submit"]',  # login tags
            '//a[@id="header-menu-toggle"]', '//*[@id="configuration"]', '//a[@id="configuration-scripts"]',   # Shyntetic Script section path
            '//*[@id="pager"]/li[1]/div/select', #Show all scripts
            '//*[@id="user-preferences-header-action-menu"]', '//*[@id="logout-header-opition"]', # Logoff
            )]

    # Parameters related to brownser
    __visible = False
    __download_path = ''

    # Constructor and destructor
    def __init__(self, username, password, xpaths, download_path, visible):
        try:
            self.__username = username
            self.__password  = password             
            self.__token = self.__get_token()             
            #Requests.packages.urllib3.disable_warnings(InsecureRequestWarning)   #Making unverified HTTPS requests is strongly discouraged.  
            self.__xpaths = xpaths
            self.__visible = visible
            self.__download_path = download_path

        except:
            return None     

    def __get_token(self): 
        url = 'https://truesightps.prod.oami.eu:8043/tsws/10.0/api/authenticate/login'
        body = {"username" : self.__username, "password" : self.__password, "tenantName" : "BmcRealm"}
        headers = {"Content-Type": "application/json"}
        req = requests.post(url, data=body, verify = False).json()
        return req['response']['authToken']


    def __get_app(self): 
        url = 'https://truesightps.prod.oami.eu:8043/tsws/10.0/api/appvis/synthetic/api/applications/getAll?isSynthetic=TRUE'
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)       
        return req.json()


    def __get_ep(self): 
        url = 'https://truesightps.prod.oami.eu:8043/tsws/10.0/api/appvis/synthetic/api/execution_plans/getAll' 
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)
        return req.json()
    

    def __get_ep_by_app(self, app_id): 
        url = 'https://truesightps.prod.oami.eu:8043/tsws/10.0/api/appvis/synthetic/api/executionplans/getAllByApplication?applicationId=' + str(app_id)
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)
        return req.json()


    def __extract_script(self, path, codepath):    
        for filename in os.listdir(path):
            try:
                with zipfile.ZipFile(os.path.join(path, filename), 'r') as myzip:
                    for info in myzip.infolist():
                        if info.filename.endswith('.bdf'):
                            myzip.extract(info, codepath)
                            new_file_name = os.path.splitext(info.filename)[0] + '.txt' 
                            os.rename(os.path.join(codepath, info.filename), os.path.join(codepath, new_file_name))
                            print ("extracted " + new_file_name + " from  " + filename )
            except:
                pass


    def scroll_to_and_click(self, driver, elem):
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

    def bulk_download(self):     
        driver_location = os.path.join('D:','lib','chromedriver.exe')
        os.environ["webdriver.chrome.driver"] = driver_location
        if self.__visible:
            driver = webdriver.Chrome(driver_location)
        else:
            chrome_options = Options()
            chrome_options.add_argument("--headless")            
            chrome_options.add_argument("download.default_directory=" + self.__download_path)                        
            driver = webdriver.Chrome(driver_location, chrome_options=chrome_options)


        for app in self.__xpaths:                        
            print ("Checking " + app[0] + "...")        
            driver.implicitly_wait(10)        
            driver.get(app[1])

            # # Perform the login
            driver.find_element_by_xpath(app[2]).send_keys(self.__username)
            driver.find_element_by_xpath(app[3]).send_keys(self.__password)
            driver.find_element_by_xpath(app[4]).click()    

            # Get to the Scripts Section
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[5]))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[6]))).click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[7]))).click()

            # Show all Scripts            
            showElements = driver.find_element_by_xpath(app[8]) 
            #self.scroll_to_and_click(driver,showElements)
            sel = Select(showElements)
            sel.select_by_value("771")
            #sel.select_by_index(2)

            # Select table 
            count_all_trs = len(driver.find_elements_by_xpath('//table//tr[@class="ng-scope"]'))
            for tr in range(count_all_trs-1):                        
                elem = driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span')
                self.scroll_to_and_click(driver, elem)
                try:            
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]/span/a').click()
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]//ul[@class="bmc-actioncolumn"]/li[3]/a').click()
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span').click()
                    print("download script num " + str(tr))
                except:
                    pass

                if tr >= 100:
                    break

            # Logoff
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[9]))).click()            
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[10]))).click()

        driver.quit()

    def distribute_ltz(self): 
        applications = self.__get_app()
        for i in applications['data']:
            if not os.path.exists(os.path.join(self.__download_path, "Active", i['displayName'])):
                os.makedirs(os.path.join(self.__download_path, "Active", i['displayName']))
                print("Created " + i['displayName'] + " folder")

            execution_plans = self.__get_ep_by_app(i['appId'])
            for ep in execution_plans['data']:
                if ep['scriptFileName'] != 'URLChecker.ltz' and ep['activeStatus'] == '1':
                    try:
                        os.rename(os.path.join(self.__download_path, ep['scriptFileName']), os.path.join(self.__download_path , "Active", i['displayName'], ep['scriptFileName']))
                    except:
                        pass        
                self.__extract_script(os.path.join(self.__download_path , "Active", i['displayName']), os.path.join(self.__download_path , "Active", i['displayName']))    





download_path = os.path.join("D:", "Prueba2") #"Truesight Scripts")
bk = itsm_scripts_management('','', download_path, True)
bk.bulk_download()
bk.distribute_ltz()