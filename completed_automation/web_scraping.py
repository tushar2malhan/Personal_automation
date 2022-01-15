import bs4
import urllib.request
import smtplib
import time
from urllib.request import Request, urlopen
import pyautogui , keyboard , requests

from win10toast import ToastNotifier

import alarm as a
import datetime,os,sys

search_cords=pyautogui.locateCenterOnScreen(r"C:\Users\Tushar\Desktop\python\pics\search.png")



def check_price():
     try:
          url =('https://www.amazon.in/Myfitfuel-Mff-Whey-Protein-Chocolate/dp/B00U5UYQKK/ref=sxin_15_trr_11364606031_4?crid=3I73LES3K9AKC&cv_ct_cx=whey+protein&dchild=1&keywords=whey+protein&pd_rd_i=B00U5UYQKK&pd_rd_r=5af8b3f3-5d4c-4f85-97fc-a625d0db8cca&pd_rd_w=DanMC&pd_rd_wg=ElB3O&pf_rd_p=e105d62b-652b-41b3-9b58-617e3a9c6f72&pf_rd_r=JCZWEN71BJCD9W10RR8H&qid=1629913915&sprefix=whey%2Caps%2C313&sr=1-4-439ac954-ad46-4ba0-bd86-480f8aab80ed')
          page = requests.get(url)
          soup = bs4.BeautifulSoup(page.content, "lxml")
          prices = soup.find(id="priceblock_ourprice").get_text()
     except:
          prices = soup.find(id="priceblock_dealprice").get_text()

     prices = float(prices.replace(",", "").replace("₹", ""))
     if prices < 1300:
          a.send_notification('MyfitFuel',f'{prices}')
          print('MyfitFuel = Whey protein on discount 😍 ',prices,end='\n\n')
          exit()
     else:
          
          a.send_notification('MyfitFuel',f'{prices}')
          print('MyfitFuel = Myfitfuel whey protein is at average price ',prices,'Nothings changed for Myfitfuel')


def check_price2():
     url_path='https://www.healthkart.com/sv/xlr8-flavoured-whey-protein-24-g-protein/SP-80127?navKey=VRNT-170727'
     url=Request(url_path,headers={'User-Agent': 'Mozilla/5.0'})

     sauce =urlopen(url).read()
     soup = bs4.BeautifulSoup(sauce, "html.parser")
     # print(soup)
     spans=soup.find_all('span', {'class' : 'prem-icon variantProductfo_prem-icon__2e31B'})
     prices =''.join([span.get_text() for span in spans])
     prices = float(prices.replace(",", "").replace("₹", ""))
     if prices < 1100:
          a.send_notification('XLR',f'{prices}')
          print(prices,'XLR Whey protein on discount 😍',end='XLR')
          exit()
     else:
          a.send_notification('XLR',f'{prices}')
          print('XLR whey protein is at average price Nothings changed for XLR ')

check_price()

url =('https://www.amazon.in/Myfitfuel-Mff-Whey-Protein-Chocolate/dp/B00U5UYQKK/ref=sxin_15_trr_11364606031_4?crid=3I73LES3K9AKC&cv_ct_cx=whey+protein&dchild=1&keywords=whey+protein&pd_rd_i=B00U5UYQKK&pd_rd_r=5af8b3f3-5d4c-4f85-97fc-a625d0db8cca&pd_rd_w=DanMC&pd_rd_wg=ElB3O&pf_rd_p=e105d62b-652b-41b3-9b58-617e3a9c6f72&pf_rd_r=JCZWEN71BJCD9W10RR8H&qid=1629913915&sprefix=whey%2Caps%2C313&sr=1-4-439ac954-ad46-4ba0-bd86-480f8aab80ed')
# page = requests.get(url)
# soup = bs4.BeautifulSoup(page.content, "lxml")
# prices = soup.find(id="priceblock_ourprice").get_text()
# //*[@id="priceblock_ourprice"]


