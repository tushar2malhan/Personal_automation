import time 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from completed_automation.Protected import credentials

HEADS_URL = 'https://heads.thinkpalm.info/Home.aspx'
TCUBE_URL = 'https://tcube.thinkpalm.info/user/projectlist'
# DOWNLOAD YOUR CHROME DRIVER FROM: https://sites.google.com/a/chromium.org/chromedriver/downloads
# DRIVER_PATH = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe' YOUR PATH HERE
driver = webdriver.Chrome(executable_path=r"C:\Users\Tushar\Downloads\chromedriver.exe")

class Think_palm():

    def tcube(self):
        ''' Operations in tcube '''
        print('Tcube Started')
        driver.get(TCUBE_URL)
        # driver.maximize_window()
        driver.find_element(By.ID,'username').send_keys(credentials.all_credentials.get('think_palm_username'))
        driver.find_element(By.ID,'password').send_keys(credentials.all_credentials.get('fortclient_password'))
        driver.find_element(By.ID,'searchform').click()
        time.sleep(5)
        driver.find_element(By.XPATH,'/html/body/div[3]/div[1]/div/div/table/tbody/tr/td[5]/a').click() # timesheet 
        print('\nWaiting for Timesheet to Load ')
        time.sleep(7)
     
        print(" Now going for attendance\n")
        table_id = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/form/table/tbody/tr[7]' )
        rows = table_id.find_elements(By.TAG_NAME, "td") # get all of the rows in the table

        ''' Iterate through the rows , find element of input by name and sent keys'''     
        for row in rows: 
            element = row.find_element(By.NAME,'row5[]')
            element.send_keys('8.5')

        driver.find_element(By.ID,'save_timesheet').click()     # SAVE TIMESHEET 

        print('\t\tTcube Attendance Marked \n\n\n\n')
        time.sleep(5)

    def heads(self):
        ''' Operations in heads '''
        print('Heads Started')
        driver.get(HEADS_URL)
        driver.find_element(By.ID,'txtUserName').send_keys(credentials.all_credentials.get('think_palm_username'))
        driver.find_element(By.ID,'txtPassword').send_keys(credentials.all_credentials.get('fortclient_password'))
        driver.find_element(By.ID,'btnLogin').click()
      
        # xpath of wfh attendance 
        try:    
            driver.find_element(By.ID,'ContentPlaceHolder1_Module2_DataListModule_ImgBtnModule_2').click() 
            driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div[2]/section/span/span[13]/div/input').click() 
        except: 
            # driver.find_element(By.NAME,'ctl00$ContentPlaceHolder1$Module2$DataListModule$ctl02$ImgBtnModule').click()
            ...

        # First click on wfh attendance
        time.sleep(5)
        WFH_ATTENDANCE = driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/nav/div/ul/li[4]')
       
        # find all li tags in WFH_ATTENDANCE 
        time.sleep(5)
        dropdowns = WFH_ATTENDANCE.find_elements(By.TAG_NAME, "li")
        links = []
        for each_dropdown in dropdowns:
            # print(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
            links.append(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
            
        
        # wfh attendance request
        driver.get(links[0]) 
        time.sleep(3)
        driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div/section/div/div[2]/input[1]').click()   # save button
        time.sleep(1)
        
        # wfh attendance list , confirm the attendance
        driver.get(links[1])     
    
        print('\t\tHeads Done, Marked attendance ')
        ...

    def main(self):
        ''' Run the operations HEADS AND TCUBE  '''
        self.tcube()
        self.heads()

tushar = Think_palm()
tushar.main()

