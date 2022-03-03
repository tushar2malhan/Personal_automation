import time 
#    pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from Protected import credentials
from selenium.common.exceptions import WebDriverException

HEADS_URL = 'https://heads.thinkpalm.info/Home.aspx'
TCUBE_URL = 'https://tcube.thinkpalm.info/user/projectlist'
# DOWNLOAD YOUR CHROME DRIVER FROM: https://sites.google.com/a/chromium.org/chromedriver/downloads
# DRIVER_PATH = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe' YOUR PATH HERE
driver = webdriver.Chrome(executable_path=r"C:\Users\Tushar\Downloads\chromedriver.exe")

class Think_palm():
    """ Think Palm Heads and Tcube Sign up Automation """

    def tcube(self):
        ''' Operations in tcube '''
        print('Tcube Started')
        if "errorPageContainer" in [ elem.get_attribute("id") for elem in driver.find_elements(By.CSS_SELECTOR,"body > div") ]:
            raise Exception( "this page is an error" )
        driver.get( TCUBE_URL )
        # driver.get(TCUBE_URL).status_code()
        # driver.maximize_window()
        driver.find_element(By.ID,'username').send_keys(credentials.all_credentials.get('think_palm_username'))
        driver.find_element(By.ID,'password').send_keys(credentials.all_credentials.get('fortclient_password'))
        driver.find_element(By.ID,'searchform').click()
        time.sleep(5)
        driver.find_element(By.XPATH,'/html/body/div[3]/div[1]/div/div/table/tbody/tr/td[5]/a').click() # timesheet 
        print('\nWaiting for Timesheet to Load ')
        time.sleep(7)
        
        print("Now going for attendance")


# WANNA click different developer story and mark attendance in different category ?   
    #   then row would row-=1 ,                                                       if developer story = 6 , then row5[]
    #   and table_id+=1 , ie  tr would increase by 1 as compared to developer story , if developer story = 6 , tr[7] 
       
        table_id = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/form/table/tbody/tr[7]' )
        rows = table_id.find_elements(By.TAG_NAME, "td") # get all of the rows in the table
       


# WANNA MISS ANY ATTENDANCE FOR THE DAY IN THE WORKING WEEK ?

        working_days = {
                "0":'Monday',
                "1":'Tuesday',
                "2":'Wednesday',
                "3":'Thursday',
                "4":"Friday"  }
       
        # This represents leave taken for the week, just type down the number , the attendance will be missed for that day
        leave = [ 1 ]   
        # Since 1 == monday and it was maha shivratri on that day , attendance is set to be missed !
        ''' Iterate through the rows , find element of input by name and sent keys'''     
        try:
            for row in rows: 
                element = row.find_element(By.NAME,'row5[]')   
                element.click()
                element.clear()
                if element.get_attribute('rel')  in working_days:
                    if element.get_attribute('rel')  in [str(i) for i in leave]:
                        element.send_keys('0')
                    else:
                        element.send_keys('8.5') 
                        # print(element.get_attribute('rel'))  #  0,2,3,4 >>> attendance for the week 
        except WebDriverException: print("Other Elements are not clickable yet")
            

        driver.find_element(By.ID,'save_timesheet').click()     # SAVE TIMESHEET 
        driver.refresh()

        print('\n\tTcube Attendance Marked \n')

    def heads(self):
        ''' Operations in heads '''
        print('Heads Started\n')
        driver.get(HEADS_URL)
        time.sleep(5)
        driver.find_element(By.ID,'txtUserName').send_keys(credentials.all_credentials.get('think_palm_username'))
        driver.find_element(By.ID,'txtPassword').send_keys(credentials.all_credentials.get('fortclient_password'))
        driver.find_element(By.ID,'btnLogin').click()
      
        # xpath of wfh attendance 
        try:    
            driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div[2]/section/span/span[13]/div').click() 
        except: 
            print("Since Fortclient not connected, xpath changed, just wait i'll check it ")
            driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div[2]/section/span/span[2]/div').click() 

        # First click on wfh attendance
        time.sleep(5)
        wfh_attendance = driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/nav/div/ul/li[4]')
       
        # find all li tags in wfh_attendance 
        time.sleep(5)
        dropdowns = wfh_attendance.find_elements(By.TAG_NAME, "li")
        links = []
        for each_dropdown in dropdowns:
            # print(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
            links.append(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
            
        
        # wfh attendance request
        
        driver.get(links[0])
        # print(links)
        time.sleep(3)
        driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div/section/div/div[2]/input[1]').click()   # save button
        time.sleep(1)
        
        # wfh attendance list , confirm the attendance
        driver.get(links[1])     
    
        print('\tHeads Done, Marked attendance ')
        driver.quit()
        ...

    def main(self):
        ''' Run the operations HEADS AND TCUBE  '''
        try:self.tcube()
        except: print('\n\tTCUBE FAILED')
        try:self.heads()
        except: print('\n\tHEADS FAILED')

tushar = Think_palm()
tushar.main()

