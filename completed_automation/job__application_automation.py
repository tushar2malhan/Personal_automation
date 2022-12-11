'''
        Description:  job Application Automation
        Date:         11/29/2022
        Status:       WIP
'''

import time
import pandas as pd
from selenium import webdriver


from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

option = Options()

option.add_argument("--disable-infobars")   # Disable "Chrome is being controlled by automated test software"
option.add_argument("start-maximized")      # open Browser in maximized mode
option.add_argument("--disable-extensions") # To disable the extension
# option.add_argument("headless")             # run in background
option.add_experimental_option("prefs", {   # REMOVE POP UP NOTIFICATIONS 
    "profile.default_content_setting_values.notifications": 1 
})
option.add_experimental_option('excludeSwitches', ['enable-logging'])

# read Excel file
df = pd.read_excel('Remote Friendly Companies.xlsx')
df = df[5:]
all_websites = [ all_websites for all_websites in  df['Website'] ] 
Region = [ Region for Region in  df['Region'] ]
Names = [ Names for Names in  df['Name'] ]

class JobApplicationAutomation:

    def __init__(self, driver):
        self.driver = driver

    def job_application_automation(self, website, region, name, positions):
        print('\n\t[*]\t', f'Applying for {name}  - {region} region\n')
        

        self.driver.get(website+'careers/') if website.endswith('/') else self.driver.get(website+'/careers/')

        time.sleep(2)

        if not self.driver.title.startswith(name) or not self.driver.title.endswith(name):
            print('\t[*]\t', f'{name}/careers/ page is not available at the moment\n')
            self.driver.get(website+'/jobs/')
            if 'Page not found'  in self.driver.title:
                print('\t[*]\t', f'{name}  Page Not Available\n')
                return False
        time.sleep(2)
        
        try:
            print(self.driver.find_element(By.XPATH,"//*[contains(text(), 'We aren’t')]").text)
            print('\t[*]\t', f'{name} Positions Not Available\
            as Company is currently not hiring.\n')
            return False
        except:
            print('\t[*]\t We are good to go, Lets find jobs for you ! \n')

        
        
        import pdb; pdb.set_trace()
        #  clicking on to view all jobs
        def openings(*word):
            import pdb; pdb.set_trace()
            
             #  check if element is visible and clickable
            try:
                time.sleep(2)

                element =  self.driver.find_element(By.XPATH, f"//*[contains(text(), {word[0]})]") 
                self.driver.execute_script("arguments[0].click();", element) \
                if element.is_displayed() and element.is_enabled() and element.text \
                is not None else None
            except:
                time.sleep(2)
                element =  self.driver.find_element(By.XPATH, f"//*[contains(text(), {word[1]})]") 
                self.driver.execute_script("arguments[0].click();", element) \
                if element.is_displayed() and element.is_enabled() and element.text \
                is not None else None
             
      
        try:
            openings('View','open positions')
        except:
            print('\t[*]\t', f'{name}  is currently not hiring.\n')
            return False
        

        time.sleep(3)

        #       Find all jobs based on ur positions list

    
        for position in positions:
            try:
                position_designation = [ i.text for i in self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{position}')]") ]
                for i in position_designation:
                    print(f'\t[*]\tPositions for {position} ', i, end=' - ')
                print('\n')
                
            except:
                print(f'\t[*]\t No positions related to {position} Field \n')


        
        # check year of experience
        # try:
        #     print(
        #         self.driver.find_element(By.XPATH,"//*[contains(text(), 'years experience')]").text.split(' ') 
        #     )
        # except:
        #     print('No Experience Required')
        import pdb;pdb.set_trace()
        
        
        #        apply for job
        # try:
        #     self.driver.find_element(By.XPATH, "//*[contains(text(), 'Apply')]").click()  
        # except:
        #     self.driver.find_element(By.XPATH, "//*[contains(text(), 'Submit')]").click()  

       

        #            Attach the resume file to the input 
        # self.driver.find_element(By.XPATH, "//input[@type='file']").send_keys(r"C:\cv\Tushar's Resume.pdf")
        

        # print( [ (i.text  ) for i in self.driver.find_elements(By.TAG_NAME, 'li')  if i.text   and ('Phone') in i.text.split(' ')]  )

        #           select dropdown and print all options
        # [ (i.text, i.click()) for i in self.driver.find_elements(By.TAG_NAME, 'option') if i.text in ( 'Male','American Indian or Alaska Native (Not Hispanic or Latino)','I am a veteran')] 


        # time.sleep(5)
        # self.driver.quit()

if __name__ == "__main__":
    driver = webdriver.Chrome(options=option, executable_path=r"C:\Users\tushar\Downloads\chromedriver.exe")
    job_application_automation = JobApplicationAutomation(driver)
    for website, region, name in zip(all_websites, Region, Names):
        job_application_automation.job_application_automation(website, region, name,
        positions = ['Software','Developer','Engineer',"Devops"])


