'''
[*] importing docker image  -> docker pull selenium/node-chrome-debug
[*] creating docker container -> docker run -d -p 4444:4444 --name selenium-node-chrome-debug selenium/node-chrome-debug
[*] starting docker container -> docker start selenium-node-chrome-debug
[*] opening browser -> chrome -p 4444

The above command starts a container from the image specified in 
detached mode (background mode). 
It also maps Port 4444 on the container to Port 4444 on your local browser.

'''
from selenium import webdriver
import time
def selenium():
    print("Test Execution Started")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options
    )
    # change or upgrade driver version in docker 
    # docker pull selenium/node-chrome-debug
    # docker run -d -p 4444:4444 --name selenium-node-chrome-debug selenium/node-chrome-debug

 
    driver.maximize_window()
    time.sleep(10)
    #navigate to browserstack.com
    driver.get("https://www.browserstack.com/")
    time.sleep(10)
    #click on the Get started for free button
    print(driver.title)
    driver.find_element_by_link_text("Get started free").click()
    time.sleep(10)
    #close the browser
    driver.close()
    driver.quit()
    print("Test Execution Successfully Completed!")