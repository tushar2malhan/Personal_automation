import os
import sys
import time
import datetime
from turtle import pd 
#    pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from modules.credentials import all_credentials
from selenium.webdriver.common.keys import Keys




def main():

    url = 'https://login.microsoftonline.com/2526ba82-27d5-4ea6-9000-8800cc349da4/reprocess?prompt=select_account&sosid=7a87274a-997e-4546-b1da-9874aec2278e&ctx=rQQIARAA42Kw0swoKSkottLXTy_QNTYz1SvKLEstSkpN0UvOz7UyMTHWD3b09TEy0A8OKBLiEhB8unlRlm6Qz9q-n__T9i1ftooRn36EXn1H5-BDjIrxlqlGxqmGlsYpJhZGqUkp5iYmSalJhomJZqZppinmqZYXGBlfMDLeYmINTszNMZrFbBFQZhHh6JEW7ubulBkZEmgcFZJeFRWSXBVZlW4SWeWX5R_ilQXkG_uFe5pGuSSX-2b5mvo72tpuYlYxMjUyS0q0MNI1Mk8x1TVJTTTTtTQwMNC1sDAwSE42NrFMSTTZxaxinmhhbmRukqhraWmeqmtiamKmm2SYAuRaAAVTk42MzC1SHzFLZWVlJeYlFqVkAMk8B2RfXmDhecXCY8BsxcHBJcAgwaDA8IOFcRErMLR0Lh_rOuH71bPnQLjuuuddDKdY9S3DXMKzgiv8S1NSs03dS_2DzcuMzEtcIiIyEwtNU_0c3SN8ggpctbNLksptTa0MJ7DxnmJj-MDG2MHOOIudYRenLtHRBQryJh5eDgYhTs7HU58-6ja75XGAl-EH3_aZH6btu9j71gMA0'
  
    driver = webdriver.Chrome(all_credentials['driver_path'])

    driver.get(url)
    # driver.minimize_window()

    time.sleep(10)
    driver.find_element(By.NAME,'loginfmt').send_keys(all_credentials['globalProtect']['email_id'])
    time.sleep(1)
    driver.find_element(By.NAME,'loginfmt').send_keys(Keys.RETURN)
    time.sleep(5)
    # import pdb;pdb.set_trace()
    driver.find_element(By.NAME,'passwd').send_keys(all_credentials['globalProtect']['password'])
    time.sleep(1)
    driver.find_element(By.NAME,'passwd').send_keys(Keys.RETURN)

    time.sleep(3)

    # click on my number ending with 72 
    print(driver.find_element(By.XPATH,"//*[contains(text(), 'Call +XX XXXXXXXX72')]").text    )
    driver.find_element(By.XPATH,"//*[contains(text(), 'Call +XX XXXXXXXX72')]").click()   
    print("wait for 20 seconds , since i called your number to verify the connection ")  
    time.sleep(25)
    driver.find_element(By.NAME,"DontShowAgain").click()
    driver.find_element(By.NAME,"DontShowAgain").send_keys(Keys.RETURN)

    try:    print(driver.find_element(By.CLASS_NAME,"button-parent").text  + '\nConnection Failed \n'),driver.quit()
    except: print("No need to Retry the connection ")



    
    
    time.sleep(1000)



# main()

