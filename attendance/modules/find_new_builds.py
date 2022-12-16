import os
import sys
import time
import datetime
from turtle import pd 
#    pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from credentials import all_credentials as credentials
from credentials import all_credentials
from vpn_connect import Connect



def send_notification(head,msg,d=3,img=None):
    # pip install win10toast
    # import win10toast
    from win10toast import ToastNotifier

    # create an object to ToastNotifier class
    n = ToastNotifier()

    n.show_toast(head, msg,duration = d )


class Builds():
    
    def check_new_builds(self):
        ''' DOCUMENTATION 
        from the flow of lates 
        > we check into success ones 
        > and add them in the dictionary
        > from success we check into the latest ones 
        > then we confirm if they are success or not    '''

        print('[*]\tChecking for new builds')
       
        # give new  URL train /path_number if new test plan comes
        url = 'https://buildbox.lab.nbttech.com/train/15428/'
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

        driver = webdriver.Chrome(all_credentials['driver_path'], options=chrome_options)
        try:
            driver.get(url)
        except WebDriverException:
            print("[*]\Builds page down \n")

        driver.minimize_window()
        ''' LOGIN '''
        driver.find_element(By.NAME,'username').send_keys(credentials['riverbed']['id'])
        driver.find_element(By.NAME,'password').send_keys(credentials['riverbed']['password'])
        driver.find_element(By.NAME,'login').send_keys(Keys.RETURN)
        time.sleep(10)
        # import pdb; pdb.set_trace()
        
        table_id = driver.find_element(By.CLASS_NAME,'table')
        rows = table_id.find_elements(By.TAG_NAME, "tr")         # get all of the rows in the table
        all_build_numbers = []
        for row in rows:      
            # print(row.text)                                     # print all the build number of the table
            all_build_numbers.append(row.text)
        try:
            test_plan_number = driver.find_element(By.XPATH,'/html/body/div/div[2]/form/div[1]/div[2]/h5/a').text
        except:
            test_plan_number = '9.14.1'         # Current Test plan ongoing 
        send_notification(test_plan_number+' # '+all_build_numbers[1],'Latest build Number',7)
     
        elements = driver.find_elements(By.XPATH,"//table[@class = 'table']//td/a") 
        all_build_box_links = []
        for element in elements:
            all_build_box_links.append(element.get_attribute("href"))

        # print(all_build_box_links)

        ''' OPEN THE LATEST    
        build box variant number 
        and find all variants from them  '''
        
        # [0] means latest build  
        driver.get(all_build_box_links[0])                        

        time.sleep(5)
        elements = driver.find_elements(By.XPATH,"//table[@class = 'table']//td/a")             # better way to get td/a from table
        all_variants_text = '\n'.join([element.text for element in elements])
        for all_variants in elements:
            all_variants_text+=all_variants.text+''               # Use import pdb;pdb.set_trace()  to print out stuff

        latest_variants = all_variants_text.replace('default','').replace('success','1').replace('/mnt/builds/steelhead/maldives/eng/9.12.2a/8/x86_64/','').split('\n')
        all_success_variants = ['image','cloud ova','hyper-v','vcx255u ova','azurevmcsh','vcx255u kvm','fvcx kvm','fvcx ova','fvcx hyper-v']
      
        d = {}
        result = True
        issues = ' '

        for i in  range(len(latest_variants)):
            if latest_variants[i] in all_success_variants:
                d[latest_variants[i]] = latest_variants[i+2] 
        
        for k,v in d.items():
            send_notification('Latest Build Unsuccessful as  variant "'+k+'"  is not successful in the build\n') if v != 'Success' else None 
            if k is not None and v is not None:
                issues += '\t'+ str(k)+' '+str(v) +' Not successful ' if v != 'Success'  else 'no issue'
            time.sleep(2)
        
        for i in all_success_variants:
            if i not in d:
                send_notification('Unsuccessful Latest Build','Latest Build Unsuccessful as  variant "'+i+'"  is not present in the build') 
                result = False 
                if i is not None:
                    issues += '\t'+str(i)+' '+' Not Present ' 

        # print(d)
        # print('result',result)
        # import pdb;pdb.set_trace()
        send_notification('Latest Build Successful','Latest build is present with all successful variants ') if result else None
        send_notification('Check Yourself',str(d),20) if result else None
        
        
        # Make Directory if not exist 
        if not os.makedirs(r'logs',exist_ok=True):
            with open(r'logs\everyday_logs_builds','a+') as f:
                f.write(f'{datetime.datetime.now().today()}:\t Latest Build Successful > {all_build_numbers[1]}  \n')\
                if result else f.write(f'{datetime.datetime.now().today()}:\t Latest build Unsuccessful > {all_build_numbers[1]}  <-- ~|~ --> {issues}\n')

            

        ''' Noob way to check variants and successful msg  -- *** not required *** '''
        # if all ([ True for i in check_success_variants if i in all_success_variants ] ):   # means all variants are present 
        #     count_of_success = 1
        #     for i in check_success_variants:
        #         if i == 'Success':
        #             count_of_success +=1
        #     print('\nBuild is Successful as all variants are present and are successful \n') if count_of_success == 9 else print('\nBuild is not Successful\n')
        # else:
        #     print('\nVariants are missing , Build not Successful \n')
        ''' Kindly ignore this for now '''

        print("\n[*]\tKindly view your Log file under log dir For today's Record \n")
          
        driver.quit()

    def main(self):
        ''' Main '''
        self.check_new_builds()


if __name__ == '__main__':
    obj = Connect('Tushar malhan')
    obj1 = Builds()
    if obj.confirmation():
        obj1.main()    
    else: 
        print('\n[*]\tLets connect the VPN first \n\n')
        obj.run()
        time.sleep(5)
        if obj.confirmation():
            obj1.main() 

    # obj1.main() 