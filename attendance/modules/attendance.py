import os ,datetime
import time
import webbrowser 
#    pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import credentials as credentials
from selenium.common.exceptions import WebDriverException
from find_new_builds import send_notification

HEADS_URL = 'https://heads.thinkpalm.info/Home.aspx'
TCUBE_URL = 'https://tcube.thinkpalm.info/user/projectlist'


# Just provide Your Credentials Here 
think_palm_username = credentials.all_credentials.get('attendance').get('username')  # 'tushar'
think_palm_password = credentials.all_credentials.get('attendance').get('password')


# DOWNLOAD YOUR CHROME DRIVER FROM: https://chromedriver.chromium.org/downloads    
# Check Your chrome Version from > chrome > settings > Help > About chrome
# DRIVER_PATH = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe' YOUR PATH HERE
class Attendance():

    def heads_tcube(self):

        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        chrome_options.add_argument("enable-automation")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("disable-features=NetworkService") 
        chrome_options.add_argument('--log-level=3')

        self.driver = webdriver.Chrome(credentials.all_credentials['driver_path'],chrome_options=chrome_options)
        
        def tcube():
            ''' 
            ************************************************************************************************************************
            Marking 
            attendance in   
            Tcube
            ************************************************************************************************************************   
            ''' 
            print('\n[*]\tTcube Started')
            try:
                self.driver.get(TCUBE_URL)
                # self.driver.maximize_window()
            except WebDriverException:
                print ("\n[*] TCUBE page down")
            self.driver.minimize_window()


            try:
                self.driver.find_element(By.ID,'username').send_keys(think_palm_username)
                self.driver.find_element(By.ID,'password').send_keys(think_palm_password)
                self.driver.find_element(By.ID,'searchform').click()
                time.sleep(5)
                self.driver.find_element(By.XPATH,'/html/body/div[3]/div[1]/div/div/table/tbody/tr/td[5]/a').click() # timesheet 
                # print('\nWaiting for Timesheet to Load ')
                time.sleep(7)
                
                # print("Now going for attendance")


            # WANNA click different developer story and mark attendance in different category ?   
            #   then row would row-=1 ,                                                       if developer story = 6 , then row5[]
            #   and table_id+=1 , ie  tr would increase by 1 as compared to developer story , if developer story = 6 , tr[7] 
            
                table_id = self.driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/form/table/tbody/tr[2]' )
                rows = table_id.find_elements(By.TAG_NAME, "td") # get all of the rows in the table
            


            # WANNA MISS THE ATTENDANCE ?

                working_days = {
                        "0":'Monday',
                        "1":'Tuesday',
                        "2":'Wednesday',
                        "3":'Thursday',
                        "4":"Friday"  }
            
                # This represents leave taken for the week
                leave = [  ]   
                # Since 1 == monday and it was maha shivratri on that day , attendance is set to be missed !
                ''' Iterate through the rows , find element of input by name and sent keys'''     
                try:
                    for row in rows: 
                        element = row.find_element(By.NAME,'row0[]')   
                        element.click()
                        element.clear()
                        if element.get_attribute('rel')  in working_days:
                            if element.get_attribute('rel')  in [str(i) for i in leave]:
                                element.send_keys('0')
                            else:
                                element.send_keys('8.5') 
                                # print(element.get_attribute('rel'))  #  0,2,3,4 >>> attendance for the week 
                except WebDriverException: print(" ")
                    

                self.driver.find_element(By.ID,'save_timesheet').click()     # SAVE TIMESHEET 
                send_notification("Tcube",'Attendance Marked',10)
                # self.driver.refresh()

                print('\n\t[*]  Tcube Done, Tcube Attendance Marked \n')
            
            except Exception as f:
                send_notification('Tcube Failed','Couldnt Mark attendance',10)
                webbrowser.open_new_tab(TCUBE_URL)
                print('\n\n\t[*]  Tcube Failed \n')
                return 'Tcube Failed'

        def heads():
            ''' 
            ************************************************************************************************************************
            Marking 
            attendance in   
            Heads
            ************************************************************************************************************************   
            ''' 

            print('\n[*]\tHeads Started\n')

            try:
                
                self.driver.get(HEADS_URL)
                self.driver.minimize_window()


                time.sleep(5)
                self.driver.find_element(By.ID,'txtUserName').send_keys(think_palm_username)
                self.driver.find_element(By.ID,'txtPassword').send_keys(think_palm_password)
                self.driver.find_element(By.ID,'btnLogin').click()

            
                # xpath of wfh attendance
                try:    
                    # self.driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div[2]/section/span/span[1]/div/input').click() 
                    self.driver.find_element(By.ID,'ContentPlaceHolder1_Module2_DataListModule_ImgBtnModule_0').click()     
                    # last 0 represents 1 image click == which image u wanna click , give the number , 0 == attendance, 1 == tour # [ imgBtnModule_0 ]
                except: 
                    print("[*] \tJust wait i'll check it \n")
                    self.driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div[2]/section/span/span[2]/div').click() 
            
            
                # First click on wfh attendance
                time.sleep(5)
                WFH_ATTENDANCE = self.driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/nav/div/ul/li[4]')
                # /html/body/form/div[3]/div[2]/div/nav/div/ul/li[4]/div/ul/li[1]/a
            
            #     # find all li tags in WFH_ATTENDANCE 
                time.sleep(5)
                dropdowns = WFH_ATTENDANCE.find_elements(By.TAG_NAME, "li")
                links = []
                for each_dropdown in dropdowns:
                    # print(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
                    links.append(each_dropdown.find_element(By.TAG_NAME, "a").get_attribute('href'))
                    
                
                # wfh attendance request
                
                self.driver.get(links[0])
                # print(links)
                time.sleep(3)
                self.driver.find_element(By.XPATH,'/html/body/form/div[3]/div[2]/div/div/section/div/div[2]/input[1]').click()   # save button
                time.sleep(1)
                
                # wfh attendance list , confirm the attendance
                self.driver.get(links[1])     
                send_notification("Heads",'Attendance Marked',10)
                print('\n\t[*]  Heads Done, Marked attendance \n')
                time.sleep(10)

            except Exception as e:
                print('\n')
                with open(r'Attendance\everyday','a+') as f:
                        f.write(f'{datetime.datetime.now().today()}:\t  Attendance Unsuccessful \n') 
                print(e)
                send_notification('Heads Failed','Couldnt Mark attendance',10)
                print('\n\n\t[*]  Heads Failed \n')
                webbrowser.open_new_tab(HEADS_URL)
                self.driver.quit()
                return 'Heads Failed'
        

        tcube()

        heads()

        self.driver.quit()
        
    def main(self):
        ''' Run the operations HEADS AND TCUBE  '''
        self.heads_tcube()
    
    def mark_attendance(self):
        '''  Calling main function '''
        self.main()

if __name__ =='__main__':
    tushar = Attendance()
    tushar.mark_attendance()


