from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import requests
import time
import os
import zipfile
import sys, argparse

class itsm_scripts_management():
    # Credentials
    __token = ''
    __username = ''
    __password = ''

    __html_path = ''
    __htmlFile = 'truesight_status.html'
    __numInactive = 0
    __numActive = 0
    __host = 'truesightps.prod.oami.eu'

    __null = None
    __download_path = ''
    __locations =  [('Truesight', 'https://truesightps.prod.oami.eu:8043/#/', 
            '//input[@placeholder="User Name"]', '//input[@placeholder="Password"]', '//button[@type="submit"]',  # login tags
            '//a[@id="header-menu-toggle"]', '//*[@id="configuration"]', '//a[@id="configuration-scripts"]',   # Shyntetic Script section path
            '//*[@id="pager"]/li[1]/div/select', #Show all scripts
            '//*[@id="user-preferences-header-action-menu"]', '//*[@id="logout-header-opition"]', # Logoff
            )]
    __apps = []

    # Parameters related to brownser
    __visible = None
    __download_path = ''

    # Constructor and destructor
    def __init__(self, username, password, download_path, visible=True):
        try:        
            item = 0
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)   # Making unverified HTTPS requests is strongly discouraged.  
            self.__username = username
            self.__password  = password             
            self.__token = self.__get_token()             
            self.__visible = visible
            self.__download_path = download_path
            self.__html_path = os.path.join(download_path, 'health')
            if not os.path.exists(os.path.join(self.__download_path)):
                os.makedirs(os.path.join(self.__download_path))
        except:
            return None     

    def __get_token(self): 
        url = 'https://' + self.__host + ':8043/tsws/10.0/api/authenticate/login'
        body = {"username" : self.__username, "password" : self.__password, "tenantName" : "BmcRealm"}
        headers = {"Content-Type": "application/json"}
        req = requests.post(url, data=body, verify = False).json()
        return req['response']['authToken']


    def __get_apps(self): 
        url = 'https://' + self.__host + ':8043/tsws/10.0/api/appvis/synthetic/api/applications/getAll?isSynthetic=TRUE'
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)       
        return req.json()


    def __get_ep(self): 
        url = 'https://' + self.__host + ':8043/tsws/10.0/api/appvis/synthetic/api/execution_plans/getAll' 
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)
        return req.json()
    

    def __get_ep_by_app(self, app_id): 
        url = 'https://' + self.__host + ':8043/tsws/10.0/api/appvis/synthetic/api/executionplans/getAllByApplication?applicationId=' + str(app_id)
        req = requests.get(url, headers={"Authorization":"authtoken " + self.__token},verify = False)
        return req.json()


    def get_report(self):                 
        if not os.path.exists(self.__html_path):
            os.makedirs(self.__html_path)
            print("Created " + self.__html_path+ " folder")

        with open(os.path.join(self.__html_path, self.__htmlFile), 'w') as f:
            f.write('''
                <style type="text/css">
                .tg  {border-collapse:collapse;border-spacing:0;margin:10px auto;width:800px}
                .tg td{font-family:Arial, sans-serif;font-size:14px;padding:4px 20px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
                .tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:4px 20px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}
                .tg .tg-1r1g{background-color:#fe0000;border-color:inherit;vertical-align:top}
                .tg .tg-us36{border-color:inherit;vertical-align:top}
                .tg .tg-ww61{background-color:#34ff34;border-color:inherit;vertical-align:top}
                .tg .tg-iwoe{background-color:#68cbd0;border-color:inherit;vertical-align:top}
                </style>
                <table class="tg">
                <tr><th class="tg-iwoe" colspan="7"><b>Truesight App Status<b></th></tr>
                <tr><td class="tg-iwoe" width="10%">Application</td>
                    <td class="tg-iwoe" width="20%">executionPlanName</td>
                    <td class="tg-iwoe" width="10%">Script</td>
                    <td class="tg-iwoe" width="20%">url</td>
                    <td class="tg-iwoe" width="10%">location</td>
                    <td class="tg-iwoe" width="10%">blackouts</td>
                    <td class="tg-iwoe" width="10%">Active</td></tr>
                ''')

            applications = self.__get_apps()                  
            for a in applications['data']: # Loop over current Aps
                eps = self.__get_ep_by_app(a['appId'])                     
                for ep in eps['data']: # Loop over EP in App selected
                    if int(str(ep['activeStatus'])) == 1:
                        url = ''
                        if ep['scriptFileName'] == 'URLChecker.ltz':
                            for at in range(len(ep['attributes'])):
                                if ep['attributes'][at]['value'].find('http') != -1:
                                    url =  ep['attributes'][at]['value']
                                    break
                        else: 
                            url = ''

                        locations = ''    
                        for at in range(len(ep['agentGroups'])):
                                locations +=  ep['agentGroups'][at]['name'] + ', '

                        blackouts = ''    
                        for at in range(len(ep['blackOuts'])):
                            if ep['blackOuts'][at]['blackoutName'] is not None:
                                blackouts +=  ep['blackOuts'][at]['blackoutName'] + ', '

                        if int(str(ep['activeStatus'])) == 1:
                            f.write('<tr><td class="tg-us36">' + a['displayName'] + 
                             '</td><td class="tg-us36">' + ep['executionPlanName'] +
                             '</td><td class="tg-us36">' + ep['scriptFileName'] +
                             '</td><td class="tg-us36">' + url + 
                             '</td><td class="tg-us36">' + locations[:-2] + 
                             '</td><td class="tg-us36">' + blackouts[:-2] + 
                             '</td><td class="tg-ww61">Active</td></tr>')
                            self.__numActive += 1

                        else:
                          f.write('<tr><td class="tg-us36">' + a['displayName'] + 
                             '</td><td class="tg-us36">' + ep['executionPlanName'] + 
                             '</td><td class="tg-us36">' + ep['scriptFileName'] + 
                             '</td><td class="tg-us36">' + url + 
                             '</td><td class="tg-us36">' + locations[:-2] + 
                             '</td><td class="tg-us36">' + blackouts[:-2] +
                             '</td><td class="tg-1r1g">Inactive</td></tr>')
                          self.__numInactive += 1
            f.write('</table>')
            f.write('<center><p>Active: '  + str(self.__numActive) + '</p><p> Inactive: ' +  str(self.__numInactive) +'</p></center>')             
            f.write( time.strftime('<center><p>%d-%m-%Y %H:%M</p></center>')) 


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


    def __enable_download_in_headless_chrome(self, driver, download_dir):
        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)


    def __open_browser(self):
        driver_location = os.path.join('D:','lib','chromedriver.exe')   
        os.environ["webdriver.chrome.driver"] = driver_location
        chrome_options = Options()
        if not self.__visible:
            chrome_options.add_argument("--headless")    
            prefs = {"download.default_directory" : self.__download_path, "download.prompt_for_download": "False"}
            driver = webdriver.Chrome(driver_location, chrome_options=chrome_options)
            driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.__download_path}}
            command_result = driver.execute("send_command", params)
        else:
            prefs = {'download.default_directory' : self.__download_path}
            chrome_options.add_experimental_option('prefs', prefs)
            driver = webdriver.Chrome(driver_location, chrome_options=chrome_options)
        return driver


    def __scroll_to_and_click(self, driver, elem):
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


    def __bulk_download(self):     
        driver = self.__open_browser()

        for app in self.__locations:                        
            print ("Checking " + app[0] + "...")        
            driver.implicitly_wait(10)        
            driver.get(app[1])

            # Perform the login
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
                self.__scroll_to_and_click(driver, elem)
                try:            
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]/span/a').click()
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]//ul[@class="bmc-actioncolumn"]/li[3]/a').click()
                    driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span').click()
                    print("downloading " + str(driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[3]').text) + " to " + self.__download_path)
                except:
                    pass
            # Logoff
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[9]))).click()            
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[10]))).click()
            print("End of searching")
        driver.quit()



    def __download_by_scripts(self, scripts_name):     
        apps_loc = {}     
        driver = self.__open_browser()

        for app in self.__locations:                        
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
            self.__scroll_to_and_click(driver,showElements)
            sel = Select(showElements)
            sel.select_by_value("771")
            #sel.select_by_index(2)
            # Select table 
            count_all_trs = len(driver.find_elements_by_xpath('//table//tr[@class="ng-scope"]'))
            for tr in range(count_all_trs-1):                        
                elem = driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[1]/span')
                self.__scroll_to_and_click(driver, elem)
                script_name =  driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[3]').text
                if script_name in scripts_name:
                    try:            
                        driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]/span/a').click()
                        driver.find_element_by_xpath('//table//tr[@class="ng-scope"][' + str(tr+1) + ']/td[2]//ul[@class="bmc-actioncolumn"]/li[3]/a').click()
                        print("downloading " + script_name + " to " + self.__download_path)
                    except:
                        pass
                else:
                    print("Searching" + "." * tr )
                self.__scroll_to_and_click(driver, elem)                        

            # Logoff
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[9]))).click()            
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, app[10]))).click()
        driver.quit()

        
    def __distribute_ltz(self, extract, apps=None): 
        applications = self.__get_apps()
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
                if extract:        
                    self.__extract_script(os.path.join(self.__download_path , "Active", i['displayName']), os.path.join(self.__download_path , "Active", i['displayName']))


    def get_scripts(self, makeTree=False, extract=False): 
        self.__bulk_download()
        if makeTree:
            self.__distribute_ltz(extract)


    def get_scripts_by_app(self, appsname, makeTree=False, extract=False):
            scripts_needed = []
            self.__apps = self.__get_apps()

            for i in appsname:
                for item in range(len(self.__apps['data'])):
                    if self.__apps['data'][item]['displayName'] == i:
                        execution_plan = self.__get_ep_by_app(self.__apps['data'][item]['appId'])
                        for item in range(len(execution_plan['data'])):
                            if execution_plan['data'][item]['activeStatus'] == "1" and execution_plan['data'][item]['scriptFileName'] != "URLChecker.ltz":                              
                                scripts_needed.append (execution_plan['data'][item]['scriptFileName'])
            print ("We are going to download: " + str(scripts_needed))            
            self.__download_by_scripts(scripts_needed)
            if makeTree:
                self.__distribute_ltz(extract)


try:    
    CLI=argparse.ArgumentParser()
    CLI.add_argument("username", help="AD login", type=str)
    CLI.add_argument("password", help="AD Password", type=str)     
    #CLI.add_argument("download_path", help="download_path", type=str)     
    CLI.add_argument("--apps",  nargs="*",  type=str,    default=[]   ) 
    CLI.add_argument('--visible', action='store_true', help="It shows the Chrome windows while it's working")
    CLI.add_argument('--organize', action='store_true', help="Organize the transactions into folders")
    CLI.add_argument('--extract', action='store_true', help="Extract the scritpt from the project")
    args = CLI.parse_args()
    
    download_path = os.path.join("D:\\Truesight Scripts") 
    bk = itsm_scripts_management(str(args.username), str(args.password), download_path, args.visible)
    if len(args.apps) == 0:
        bk.get_scripts(args.organize, args.extract)
    else:
        bk.get_scripts_by_app( args.apps, False, False)
    bk.get_report()    
except:
    e = sys.exc_info()[0]
    print (e)

# Uso :  python -u itsm_scripts_management.py user pass --visilble  --organize --extract
