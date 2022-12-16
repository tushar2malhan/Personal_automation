
import os
import time
import datetime
import webbrowser 
#    pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from vpn_connect import Connect
from credentials import all_credentials
from find_new_builds import send_notification

class Fits():

    def main(self):
        ''' Check success or failure for all
        the fits tests '''
        url = 'http://jenkins.lab.nbttech.com/view/eng-salesmen-FIT/'

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
            driver.get( url )
        except WebDriverException:
            print("[*]\tFits page down \n")

        driver.minimize_window()
        time.sleep(10)

        print('\n[*]\tChecking for  fits Tests plan \n')
        image_elements = driver.find_elements(By.XPATH,"//table[@class = 'sortable pane bigtable stripped-odd']//td/img")
        
        all_alt_text = []
        for image in image_elements:
            all_alt_text.append(image.get_attribute('alt').strip())
        if 'Failed' in all_alt_text or 'Unstable' in all_alt_text:
            send_notification("Fits Unsuccessful",'One Fit Unsuccessful',10)
            webbrowser.open(url) 
        else: send_notification('Success For All Fits',"Successful Fits",10)

        if not os.makedirs(r'Fits',exist_ok=True):
            with open(r'Fits\everyday_Fits_logs','a+') as f:
                f.write(f'{datetime.datetime.now().today()}:\t Fits Unsuccessful \n') if 'Failed' in all_alt_text or 'Unstable' in all_alt_text else f.write(f'{datetime.datetime.now().today()}:\t Fits Successful \t\n')

        print("\n[*]\tKindly Check your  Fits dir for logs\n\t")
        return True if 'Success' in all_alt_text else False
        
    def __str__(self) -> str:
        return '''\n\t Checking status of all Fits tests '''

if __name__ == '__main__':

    f = Fits()
    vpn_connect = Connect('Tushar malhan')
    
    if vpn_connect.confirmation():
        f.main()
    else: 
        print('\n[*]\tLets connect the VPN first \n\n')
        vpn_connect.run()
        time.sleep(5)
        if vpn_connect.confirmation():
            f.main()


