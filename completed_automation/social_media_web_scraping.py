from re import I
import time
import sys 
import json
import pyautogui
from selenium import webdriver
import credentials 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


u_input = input("Which Social Media account  would you require information for ?: \n\n\
   \t Instagram \t Facebook \t Twitter \t Linkedin \n").lower().strip()
linkedin_email = credentials.all_credentials['linked_email']
linkedin_password = credentials.all_credentials.get('linked_password')
# data = {}

def user_information(username):
    """ Display user information from
    their social media accounts """
    driver = webdriver.Chrome(executable_path=r"C:\Users\Tushar\Downloads\chromedriver.exe")
    try:
        if u_input.startswith('i'):
            print('Instagram\n')
            url = f"https://www.instagram.com/{username}/"
            driver.get(url)
            name = driver.title
            try:
                # here u copy the classname of the element and then search it by driver
                # remember u want text or get_attribute('src') == image
                name = driver.find_element(By.CLASS_NAME,'XBGH5').text
            except:
                name = driver.find_element(By.XPATH ,'//*[@id="react-root"]/section/main/div/header/section/div[1]/h2').text
                name = driver.find_element(By.CLASS_NAME,'_2s25').text
            try:
                profile_pic = driver.find_element(By.CLASS_NAME, "be6sR").get_attribute('src')
            except:
                profile_pic =driver.find_element(By.CLASS_NAME, "_6q-tv").get_attribute('src')
            try:
                total_posts = driver.find_element(By.CLASS_NAME, "g47SY").text
            except:
                print('Couldnt fetch the total posts of the User from Instagram')
            try:
                followers = driver.find_element(By.CLASS_NAME, "_81NM2").text
            except:
                followers = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').text
            # data[f'total_posts_of_{username}'] = total_posts
            # data[f'followers_of_{username}'] = followers
            
            # print(f'Profile pic URL is \t',profile_pic,end='\n\n')
            print(f'Total posts are \t',total_posts,end='\n\n')
           
        
        elif u_input.startswith('f'):
            print('Facebook\n')
            wait = WebDriverWait(driver, 10)
            url = f"https://www.facebook.com/"
            driver.get(url)
            
            """ here we try to find element by class name by looking at page source and we get attribute
                 we make some time with sleep so that it doesn't break the code'
                 xlink:href  is the attribute of the image we want from FB 
                 IF U DONT FIND UR USERNAME HERE , TRY USING name.sername
                 name = driver.title """
            """ LOGIN FIRST """

            driver.find_element(By.ID,'email').send_keys(credentials.all_credentials['fb_email'])
            driver.find_element(By.ID,'pass').send_keys(credentials.all_credentials['fb_password'])
            try:
                driver.find_element(By.CSS_SELECTOR,'.'+'.'.join('_42ft _4jy0 _6lth _4jy6 _4jy1 selected _51sy'.split(' '))).click()
            except:driver.find_element(By.ID,'u_0_d_Mc').click()
           
            time.sleep(10)
            try:
                pyautogui.click(pyautogui.locateOnScreen(r'C:\Users\Tushar\Desktop\cloud_next\images\allow_blue.png',confidence = .8))
                time.sleep(1)
                pyautogui.click(pyautogui.locateOnScreen(r'C:\Users\Tushar\Desktop\cloud_next\images\fb_white.png',confidence = .8))
                time.sleep(1)
                url_2 = f"https://www.facebook.com/{username}/"
                pyautogui.write(url_2)
            except :print('Stay on the Page else I cant write the url')
            pyautogui.press('enter')
            name = driver.title         # .split('Facebook')[0].split('|')[0]
            time.sleep(10)

            profile_pic = [i.get_attribute('xlink:href') for i in driver.find_elements(By.TAG_NAME,"image")]
            time.sleep(2)
            if profile_pic == []:
                profile_pic = driver.find_element(By.CLASS_NAME,'_2dgj').get_attribute('href')
               
            try:
                # this for a PAGE in fb, u get number of followers from the page
                followers_of_page =[i.text for i in driver.find_elements_by_css_selector('.'+'.'.join('d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh jq4qci2q a3bd9o3v b1v8xokw oo9gr5id'.split(' '))) if i.text.endswith('like this')]
                if followers_of_page :
                    print('Total followers of page are ',''.join(   followers_of_page     ))
                    followers = followers_of_page[0].split(' ')[0]
                else:
                    # this for a General User whose profile is not locked in fb, u get number of followers from the page
                    print('\n Not a Page')
                    followers =  driver.find_element(By.CSS_SELECTOR,'.'+'.'.join('d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh e9vueds3 j5wam9gi b1v8xokw m9osqain'.split(' ')) ).text                                     
                    if followers.isdigit():
                        int(followers)
                        print("General User\n")
                    else:
                        raise Exception
            except:
                # this for a CELEBS PAGE, u get number of followers from the page
                followers = driver.find_element(By.CSS_SELECTOR,'.'+'.'.join('oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p'.split(' '))).text
                if followers.split(' ')[0].split('M')[0].isdigit():
                    print("\n\t But Its a Celebs Page \n ")
                else:
                    # profile hidden , cant do anything
                    followers = 'Hidden'
                    print('Profile is locked\nCant show friends as profile is Locked OR Profile is Public ,\n You need to make them friend first')
                

        elif u_input.startswith('t'):
            """
            SO u wanna get element having multiple classes ? 
            - Followers classname refers to the element having multiple classes.which refers
            to a single element, hence we used CSS selector or can use xpath
            where we need to join classes with . DOT .  
            but not for XPATH - was not working properly
            """
            print('Twitter\n')
            url = f"https://www.twitter.com/{username}/"
            driver.get(url)
            time.sleep(7)
            followers_class_name = '.'+ '.'.join('css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0'.split(' '))  
            total_words_list = [total_followers.text for total_followers in driver.find_elements_by_css_selector(followers_class_name)]
            time.sleep(5)
            followers =' '.join([ total_words_list[i-1] for i,word in enumerate(total_words_list) if word == 'Followers'])
            name = total_words_list[10] if not '' else total_words_list[11]

            if name is  None or name == '':
                print('\nCan fetch the name\n')
            time.sleep(5)
            profile_pic = driver.find_element(By.CLASS_NAME,'css-9pa8cd').get_attribute('src')
            # data[f'followers_of_{username}'] = followers

        elif u_input.startswith('l'):
            """ here we have to signin first and
            then click on url to search the name in the linkedin """
            print('Linkedin\n')
            # url = f"https://www.linkedin.com/"   
            url = f'https://www.linkedin.com/in/{username}/' 
            driver.get(url)
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR,'.authwall-join-form__form-toggle--bottom.form-toggle').click()
            
            time.sleep(3)
            driver.find_element(By.ID,'session_key').send_keys(linkedin_email)
            driver.find_element(By.ID,'session_password').send_keys(linkedin_password)
            driver.find_element(By.CLASS_NAME,'sign-in-form__submit-button').click()
            time.sleep(10)
            pyautogui.click(pyautogui.locateOnScreen(r'C:\Users\Tushar\Desktop\cloud_next\images\linkedin_in_url_white.png',confidence = .8))
            pyautogui.write(url)
            pyautogui.press('enter')
            time.sleep(15)
            followers = driver.find_element(By.CLASS_NAME,'t-bold').text
            name = driver.find_element(By.CLASS_NAME,'pv-text-details__left-panel').text
            profile_pic = driver.find_element(By.ID,'ember33').get_attribute('src')
            # data[f'followers_of_{username}'] = followers
            time.sleep(50)
        
        else:sys.exit("Invalid input")
        try:
            print(f'Username is \t\t',name,end='\n\n')
            print(f'Profile pic URL is \t',profile_pic,end='\n\n')
            print(f'Total Followers are \t\t',followers,end='\n\n')
            # data[f'name_of_{username}'] = name
            # data[f'profile_pic_of_{username}'] = profile_pic
        except:
            print('\tCant return name and profile URL')
    
        driver.close()
        return name
    
    except :
        driver.close()
        print(f'{username}\t Check The Username Again\n ')
        return(f'\n\n Issue with User named -> {username} for getting the information for {u_input}')


names = [ 
        # 'tusharmalhan',
        # 'vindiesel',
        # 'rahul.vij.127',
        # 'ok',
        # 'tusharmalhan','iamsrk',
        # 'cristiano',
        # 'ktrtrs',
        # 'bajaj',
        # 'virat.kohli',
        # 'ronaldo','iamsrk',
        # 'rahul_vij','egg', 'Tushar79958956',
        ]
[user_information(name) for name in names]