
import os , shutil
from re import A 
import time
import keyboard
import pyautogui
import webbrowser
import sys
from PIL import ImageGrab

import pytesseract as tess
import datetime
tess.pytesseract.tesseract_cmd =r'D:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image   #pip install SpeechRecognition


import datetime
import dateutil.relativedelta as rdelta  #pip install python-dateutil
from datetime import timedelta

day=datetime.datetime.now().day
day1 = f'0{day}' if day <=9 else day
month = datetime.datetime.now().month
month1 = f'0{month}' if month <= 9 else month
month1_name= datetime.datetime.now()

today = datetime.date.today()
last_monday = today + rdelta.relativedelta(days=-1, weekday=rdelta.MO(-2))
coming_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)

yesterday = today - timedelta(days = 1)



# passwords for all servers
password='traceart@1234'
password_47 ='traceart@123'
password_20 ='Secure@dmin@2021'
password_67 ='Secure@dmin@2021'
job_file_path =r'D:\Users\tusha\Desktop\PYTHON\job_file.txt'

#   47 Queries 

gupshup =(f"""

  select * from GupshupSendMessageResponse with(nolock) where Source='SCHEDULER'
   and CreatedDate >= '2021-{month1}-{day1} 00:00:00.000'  and  TemplateID ='RNLIC_SD022' 
  --and ReponseID not like '%success%'
   order by CreatedDate  desc  -- pendinf _issurance  -- advisor and debug sm,bm  

  select * from GupshupCallBack order by CreateDate desc


  select * from GupshupSendMessageResponse with(nolock) where  cast(CreatedDate as date) ='2021-{month1}-{day1}' 
   and  TemplateID ='rnlic_pendingpolicy01'  --and ReponseID not like '%success%'
   order by CreatedDate  desc  --ch  -- dh 


  select * from GupshupSendMessageResponse with(nolock) where Source='FTNRSCHEDULER' 
  and CreatedDate >='2021-{month1}-{day1} 00:00:00.000'     --and ReponseID not like '%success%'  
   order by CreatedDate  desc  -- FTNR

  -- select * from GupshupMasterTemplates with(nolock) where TemplateID ='rnlic_nudge_2_escalate_rm_revised'
   
   --select * from tblWhiteListDetails with(nolock) where TemplateName ='rnlic_nudge_2_escalate_rm_revised'

   SELECT Wl.pkRowID, [ReferenceName],[TemplateName],[Type],[Language],[TemplateText],CASE   
  WHEN wl.[IsActive]=1 THEN 'Submitted'   WHEN Wl.[IsActive] = 0 
  THEN 'Deleted' END AS [PartnerApproval],RequestedBy,dm.DepartmentName,dm.CostCenter,[UpdatedOn] FROM.[WhatsAppPortal].[dbo].[tblWhiteListDetails] 
  wl with(nolock) inner join  WhatsAppPortal.dbo.AspNetUsers usr with(nolock) on wl.RequestedBy=usr.UserName 
  inner join WhatsAppPortal.dbo.tblDepartmentMaster dm with(nolock) on usr.fkDepartment=dm.pkRowID where InternalApproval='S' and ((PartnerApproval='P' 
  and wl.IsActive=1) or (PartnerApproval='Y' and wl.IsActive=0)) Order By UpdatedOn desc


  SELECT Wl.pkRowID, [ReferenceName],[TemplateName],[Type],[Language],[TemplateText],CASE   
   WHEN wl.[IsActive]=1 THEN 'Submitted'    WHEN Wl.[IsActive] = 0 THEN 'Deleted' END AS 
   [PartnerApproval],RequestedBy,dm.DepartmentName,dm.CostCenter,[UpdatedOn] 
   FROM.[WhatsAppPortal].[dbo].[tblWhiteListDetails_YM]  wl with(nolock) inner join  
   WhatsAppPortal.dbo.AspNetUsers usr with(nolock) on wl.RequestedBy=usr.UserName inner join 
   WhatsAppPortal.dbo.tblDepartmentMaster dm with(nolock) on usr.fkDepartment=dm.pkRowID where 
   InternalApproval='S' and ((PartnerApproval='P' and wl.IsActive=1) or (PartnerApproval='Y' 
   and wl.IsActive=0)) Order By UpdatedOn desc


  select * from GupshupSendMessageResponse  with(nolock)  where    CreatedDate>='2021-{month1}-{day1} 00:00:00.000'   and ReponseID not like '%success%'


  select * from WhatsAppLog with(nolock) where EventName like '%error%' and EventName not like '%318%' and EventName not like '%6. Record inserted Error successfully%' 
  and Date between '{yesterday} 00:00:00.000'and '2021-{month1}-{day1} 13:30:00.000' order by Date desc

  select TemplateID,count(TemplateID) from GupshupSendMessageResponse with(nolock) where CreatedDate>='2021-{month1}-{day1} 00:00:00.000' and 
  ReponseID like '%error | 318 | Message does not match WhatsApp HSM template.%' group by TemplateID 

  select * from WhatsAppPortal.dbo.[tbl_log] where  Error not  like 'Execution Timeout Expired '  and  convert(date,Date)='2021-{month1}-{day1}' order by pkid desc

  
  -- select * from tblWhiteListDetails with(nolock) where TemplateName like '%personalised%'

   --select * from GupshupMasterTemplates with(nolock) where TemplateID like '%rnlic_NONPAR_PWT_Revised%'


  -- select * from tblWhiteListDetails with(nolock) where TemplateName ='rnlic_nudge_2_bm'      -- this template is inactive 

   
    SELECT  [Id]
      ,replace(Substring([RequestURL],charindex('filename',[RequestURL]),len([RequestURL])-charindex('filename',[RequestURL])+1),'filename=','') as PolicyNo
      ,[RequestURL]
      ,[RecipientNumber]
      ,[ReponseID]
      ,[SendTexttotheCustomer]
      ,[CreatedDate]
      ,[Source]
      ,[ActualMessageSendtoCustomer]
      ,[TemplateID]
      ,[MessageID]
      ,[TransactionID]
      ,[FailedTime] 
      ,[SentDateTime] 
      ,[ReadDateTime] 
      ,[DeliveryDateTime] 
      ,[MethodName]
  FROM.[dbo].[GupshupSendMessageResponse] with(nolock) where Source='PolicyDoc'
   and CreatedDate between '{yesterday} 14:00:00.000' and '2021-{month1}-{day1} 14:00:00.000'   
  
  select * from GupshupMasterTemplates order by CreatedDate desc

  
    
    -- drop table #CountOfMessages
    select [TemplateID],count([TemplateID]) as [Total] into #CountOfMessages from [GupshupSendMessageResponse] 
    with(nolock) where ReponseID like '%success%' and CreatedDate>=cast(getdate()-30 as date) Group By[TemplateID] 

	 -- drop table #FinalCount
      select distinct cm.TemplateID,cm.Total,gt.POC,gt.CostCentre into #FinalCount from [#CountOfMessages]cm left join [GupshupMasterTemplates]gt on cm.TemplateID=gt.TemplateID;
      
      -- 1152577  1152577
      select TemplateID,Total ,POC,CostCentre from #FinalCount union all select '                  Total',sum(Total),'','' from #FinalCount

      select * from #FinalCount

      --drop table #POCWiseCount

      select POC,sum(Total) as Total into #POCWiseCount from #FinalCount group by POC;

      select * from #POCWiseCount
      
      select POC,Total from #POCWiseCount union all select '         Total',sum(Total) from #POCWiseCount


   -- when other get approves, update their qr as well , ask permission first
	select * from GupshupMasterTemplates wiht(nolock) where TemplateID 
	in ('Unclaim_2a_connect','Unclaim_3_bankupdate_options','Unclaim_2_contact','Unclaim_1_details')



    SELECT [ID],
    ''''+[RecipientNumber]+'''' AS [RecipientNumber],
    [CreatedDate],
    [Source],
    [SendTexttotheCustomer] as Message,
    ''''+[TransactionID] +'''' AS [TransactionID],
    [FailedTime],
    [SentDateTime],
    [ReadDateTime],
    [DeliveryDateTime],
    [MethodName] 
    FROM.[dbo].[GupshupSendMessageResponse] with(nolock) where TemplateID in('rnlic_retention_WA_CALLBACK_CRS','rnlic_Nominee Name_MSG','rnlic_Covid_MSG') and 
    CreatedDate between  '{last_monday} 00:00:00.000'and '{today} 13:30:00.000'  Order By ID desc

    """)
ods_data=(f'''
    select distinct WhatsApp_Response from CustomerSMSDetails with(nolock) where 
    CreatedDate  between '{yesterday} 10:00:00.000'and '2021-{month1}-{day1} 10:00:00.000'  and WhatsApp_Status='Y' 
    -- select * from CustomerSMSDetails where WhatsApp_Status='Y' and convert(date, WhatsApp_SendDate)='2021-{month1}-{day1}' order by CreatedDate desc 

     select distinct WhatsApp_Response from CustomerSMSDetails where WhatsApp_Status='Y' and
		    convert(date, WhatsApp_SendDate)='2021-{month1}-{day1}'

     ''')
ymbot=(f'''
 
   select * from OutMessages with(nolock) where  CreatedOn > '2021-{month1}-{day1} 00:00:00.000'  order by RowID desc  
 	

   select * from DeliveryStatus with(nolock) where FailureCause is not null and convert(date,SentOn) >= '2021-{month1}-{day1} 00:00:00.000'

   -- 4  encach   ,   9 -- bday1_wish_nudge    , 25 -ecs


   select count(TemplateID) as COUNTT , TemplateID  from OutMessages with(nolock)   where  CreatedOn > '2021-{month1}-{day1} 00:00:00.000'
    and TemplateID in(4,9,25)
    group by TemplateID 


   select count(TemplateID) as COUNT_in_ym , TemplateID,TriggerStatus  from OutMessages with(nolock)   where  CreatedOn >
    '2021-{month1}-{day1} 00:00:00.000'  and TemplateID in(25,9,4) group by TemplateID,TriggerStatus
	



    select * from LogWrites with(nolock) where convert(Date,LastUpdatedOn)='{month1_name.strftime("%b")} {day1} 2021' 
	 and Excep   not like          '%Invalid RecipientNumber Function=NumberCheck%'     
	  and Excep   not like'%Invalid WhatsApp message%'  and FunctionName not like '%callback%'  order by RowId  desc
      
      select MobileNo,count(MobileNo) from OutMessages  with(nolock) where TriggeredOn>='2021-{month1}-{day1} 00:00:00.000' group by MobileNo having count(1)>1
         
     SELECT distinct [MobileNumber] FROM [NudgeSystem].[dbo].[Entity] with(nolock) where MobileNumber in ('without 91') group by MobileNumber having count(1)>1
     
     select distinct MobileNo from OutMessages with(nolock) where MobileNo in( 
	
	)
        and TriggerStatus='fail' and TriggeredOn>'2021-{month1}-{day1} 00:00:00.000' 

'''
)



agree =['yes', 'y','ok','yeah','yup']


# Take a screenshot  and saving to ur local system  
def screenshot(filename):
    save_path=  (fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\{filename}_{datetime.datetime.today().day}.jpg') 
    snapshot = ImageGrab.grab()
    snapshot.save(save_path)
    print(' Done saved ur screenshot ')
    time.sleep(10)

# open the server event viewer
def eventvwr():           # opens only the event viewer , under windows logs then applications
    eventvwr = input('\nwanna start the event viewer \t')
    if eventvwr in agree:
                pyautogui.click(350,50)                # SAFE coordinates to go back to server to open anything
                pyautogui.hotkey('win', 'r')
                time.sleep(2)
                keyboard.write('eventvwr')
                time.sleep(2)
                pyautogui.press('enter')
                time.sleep(20)
                pyautogui.doubleClick (x=61, y=143)    #  go to windows logs
                time.sleep(2)
                pyautogui.doubleClick (x=84, y=163)    # go to applications
                # time.sleep(60)                       # uncomment this accordingly
                # pyautogui.click (x=573, y=272)         # click on any event viewer for any app  inorder to scroll down

# open the server task scheduler
def taskscheduler():
    task = input('Open the task scheduler ? ')
    if task in agree:
        pyautogui.click(350,50)                  # safe coordinates
        pyautogui.hotkey('win', 'r')
        time.sleep(2)
        keyboard.write('taskschd.msc')
        pyautogui.press('enter')
        time.sleep(7)
        pyautogui.doubleClick(x=66, y=127)   # task scheduler library
        time.sleep(10)
        pyautogui.click (x=621, y=152)       # click randomy on any task scheduler
        pyautogui.click (x=621, y=152)       # click randomy on any task scheduler
        pyautogui.press('down', presses=20)   # scrolling down 

def login():
    print('I hope u provided the Pin\n\n')
    citrix_input = input('Have you logged into the cirtix gateway  ? \t')
    if citrix_input not in ['yes','ok','done','Done','y','yes','']:
        try:
            webbrowser.register('chrome',None,webbrowser.BackgroundBrowser(r'D:\Program Files\Citrix\Secure Access Client\nsload.exe '),1)
            os.startfile(r'D:\Program Files\Citrix\Secure Access Client\nsload.exe')                  # open citrix
            time.sleep(7)
            pyautogui.click(x=776, y=307)
            pyautogui.click(x=759, y=374)
            time.sleep(5)                       # making u log to connect to vcap server 
            pyautogui.click(x=657, y=260)

            pyautogui.click(x=687, y=411)   # username
            keyboard.write('9043511')
            time.sleep(2)

            pyautogui.click(x=696, y=456)   # password
            keyboard.write(password)
            time.sleep(2)
            
            a=input('> ')
            pyautogui.click(x=746, y=194)
            pyautogui.click(x=685, y=500)   # passcode
            keyboard.write(a)
            time.sleep(2)

            pyautogui.click(x=592, y=174)   # go back to citrix gateway 
            pyautogui.click(x=948, y=572)   # submit button
        except:
            print('you have not provided the pin')
    else:
        print('Citrix logged in now ')


    time.sleep(5)

    arcon_input = input('logged in Arcon ? ')
    if arcon_input not in ['yes','ok','done','Done','y','yes']:
        ie = webbrowser.get("D:\Program Files\Internet Explorer\iexplore.exe")
        ie.open_new('https://rclpim.reliancecapital.com/frmLoginACMO.aspx')
        time.sleep(10)

        pyautogui.click(  x=679, y=89  )    # Full screen 
        time.sleep(2)  
        pyautogui.doubleClick( x=229, y=355 )   # more info in internet
        time.sleep(2)
        pyautogui.doubleClick( x=339, y=485  )   # go on to the webpage 

        time.sleep(25)
        
        pyautogui.click(x=663, y=304)  
        keyboard.write('9043511')        # ARCON USERNAME 
        time.sleep(1)
        pyautogui.click ( x=651, y=361 )  
        keyboard.write(password)       # ARCON PASS
        time.sleep(1)
        pyautogui.click (x=841, y=482)     # login

        time.sleep(6)
        pyautogui.click (x=559, y=322)     # OTP for challenge
        ai=input('> ')
        pyautogui.click (x=559, y=322)     # OTP for challenge
        keyboard.write(ai)         # ARCON type OTP - we enter OTP
        time.sleep(2)
        pyautogui.click (x=431, y=423)     #  validate OTP and submit
        pyautogui.click (x=410, y=420)     #  validate OTP and submit
        time.sleep(16)
        print('getting you inside the Cloud')
        pyautogui.click (x=532, y=260)     #      #  SELECT in service type
        time.sleep(3)
        pyautogui.click (x=501, y=325)     #  chooding  WINDOWS RDP service for ur servers
        
        time.sleep(15)
        print('\nYou can start the selection Process\n')

    else:
        print('\nlogged in arcon as well\n')

# open the  sql server
def sql_server():
    pyautogui.hotkey('win')
    time.sleep(2)
    keyboard.write('sql')
    time.sleep(3)
    pyautogui.moveTo(x=212, y=192)      # right click
    pyautogui.click(button='right')  # right-click the mouse
    time.sleep(3)
    pyautogui.click(x=459, y=660)     # run as administrator

checklist = ['wait','ruko','let me check','checking','']

print('')
ans = input('wanna login to arcon and citrix ? ').lower()
if ans in ['yes', 'y','ok','yeah','yup']:
    login()
print('')

''' selection state '''
server_coordinates ={
    89:{'x':1314,'y':453},     # second 89 instance
    47:{'x':1310,'y':495},
    78:{'x':1316,'y':537} ,
    
    67:{'x':1319,'y':331} ,
    20:{'x':1317,'y':405},
    114:{'x':1314,'y':448}   # need to scroll  for all 3 servers
}

second_half_servers = [114,67,20]

''' servers includes 47 78 20 114 where passwords are involved '''
def go_to_server(x=0,y=0):
    server = int(input(' select your server from 47 78 20 114 67 89 \t ~ '))

    if server in second_half_servers:      #         II  half of the server
        pyautogui.click (x=1266, y=161)     #  go back to arcon 
        time.sleep(2)
        pyautogui.scroll(-1000)
        time.sleep(2)
        x= server_coordinates[server].get('x')
        y= server_coordinates[server].get('y')
        time.sleep(2)
        pyautogui.click (x=850, y=645)                                   #  ur scrolled down now coordinates changed
        pyautogui.click (x=850, y=645)                                   #  ur scrolled down now coordinates changed
        pyautogui.click (x,y) 
        time.sleep(5)  
        pyautogui.click (x=457, y=295)                                  #  selecting option to open
   
    elif server not in second_half_servers : #  == 47  | 78 | 114           #   I   half of the server  
        pyautogui.doubleClick(x=1210, y=667)    #                           safe coordinates part II
        pyautogui.scroll(1000)
        pyautogui.scroll(1000)
        x= server_coordinates[server].get('x')
        y= server_coordinates[server].get('y')            
        pyautogui.click (x=1173, y=177)     #  go back to arcon 
        pyautogui.click (x,y) 
        time.sleep(1)
        pyautogui.click (x,y) 
        time.sleep(4)  
        pyautogui.click (x=457, y=295)     #  selecting option to open

    print(f'wait connecting to the {server} server  ')
        
    def review(review_statement):
        with open(job_file_path,'a')as f:
                f.write(review_statement)
                f.write('\n')

    def file_explorer():              #  IF U WANNA OPEN FILE EXPLORER THEN , JUST WRITE PATH AFTER THIS FUNC with keyboard.write('path') 
        explore = input('\nwanna explore the files \t')
        if explore in agree:
            pyautogui.click(350,50)
            pyautogui.hotkey('win', 'e')
            time.sleep(2)
            if server==78:
                pyautogui.doubleClick (x=513, y=178)      # search bar for location of files for server 78
            elif server == 114:
                time.sleep(5)
                pyautogui.doubleClick (x=512, y=95)      # search bar for location of files  for server 114
            time.sleep(2)
            pyautogui.hotkey('ctrl','a')      
            pyautogui.press('space')           # for backspace so that u can give ur path 
            time.sleep(3)
            return True
        else:
            print('\nok not opening the file explorer , moving on to the next command')
            return False

                            
#                Till here we are connected to the server  and LETS SEE HOW we need to go inside the server 
  
    if server == 47 :
        time.sleep(80)
        pyautogui.click (x=473, y=375)     #  ACCEPTANCE 
        time.sleep(4)
        pyautogui.click (x=682, y=269)      # ok to approve
        pyautogui.click (x=682, y=269)      # ok to approve
        time.sleep(2)
        pyautogui.doubleClick (x=716, y=282)      # click on input box
        keyboard.write(password_47)      #  server 47 password  
        time.sleep(2)
        pyautogui.click (x=923, y=279)      # click go to enter in ur server

        
       
        query_ods = input('\nODS > if u are on the SQl server should i manually update the queries ')
        if query_ods in  agree:
            pyautogui.click(x=656, y=255)    # randomly select middle click 
            pyautogui.hotkey('ctrl','a')      
            pyautogui.press('space')           # for backspace so that u can give ur query
            time.sleep(3)
            keyboard.write(ods_data)    # will update ods queries 

        query_ym = input('\nYMBOT > if u are on the SQl server should i manually update the queries  ')
        if query_ym in  agree:
            pyautogui.click(x=656, y=255)    # randomly select middle click 
            pyautogui.hotkey('ctrl','a')      
            pyautogui.press('space')           # for backspace so that u can give ur query
            time.sleep(3)
            keyboard.write(ymbot)               # will update ymbot queries 
        
        query_gs = input('\nGUPSHUP > want this query ? ')
        if query_gs in agree:
            print('\t\t\rPrinting gupshup queries for you \n')
            print(gupshup)




        ftnr_ans = input('\nWas FTNR  ok ? ')                                             # FTNR
        if ftnr_ans in agree:
            count = int(input('Count of ftnr ? '))
            review(f' ftnr = ok =={count}\n') 
        elif ftnr_ans in checklist:
            print('ok ill wait ')
        else:
             review('Check schdeulers for FTNR as some issue is witnessed\n')
            

        ch_dh_ans = input('\nWas CH and DH ok ? ')                                          # CH DH 
        if ch_dh_ans in agree:
            review(f' chdh  == ok  \n')  
        elif ch_dh_ans in checklist:
            print(' ok ill wait ')
        else:
            review('Check schdeulers for ch and dh as some issue is witnessed\n')
            
        pi_ans = input('\nI hope Pi did not had any failure messages and  PI is ok ! \t')   #  PI
        if pi_ans in agree:
            count = int(input('Count of Pending issurance ? '))
            review(f' pi == {count} == ok \n') 
        elif pi_ans in checklist:
            print(' ill wait ')
        else:
            review('check 20 server for Pending issurance \n')

        whitelist_ans= input('Is whitelist markup set up set for respective date ? ')       # whitelist
        review('whitelist == ok')if whitelist_ans in agree else review('whitelist markup not set properly')
            
        
        countt_ods = input('Ods count today ? ')                            # ASK ABOUT ODS AND PD 
        countt_pd = input('policy doc count today ? ')
        if countt_ods in checklist or countt_pd in checklist:
            print(' ok I"ll wait for the actual count ')  
        elif int(countt_ods) == int(countt_pd):
            review(f'Todays ods, pd ==ok == count =={countt_pd}\n')  
        else:
            review('check it manually i think scheduler of ods must have ran exceeding time period 2:30 pm \n')

            

        if datetime.datetime.now().hour >= 16:                                        # ASK YM BOT
            ym_ans = input('Was ym bot ok ?')
            review(f' ymbot = no error log file , logwrites = ok, ds ok \n')
        else:
            print('\nI"ll ask  about ym bot after 4 pm\n')
        
        gupshup_ans= input('\nWas gupshup ok ? ')                                # gupshup review

        if gupshup_ans in agree:
            review(f' gupshup ==ok \n')
        elif gupshup_ans in checklist:
            print('ok u can update it then')
        else:
            review('Issue in Gupshup')
        
        overall_47_review = input('\nAny issue overall in any application for 47 server| YES OR NO ? | \n')
        if overall_47_review in agree:
            ans_47 = input('\nYes what is it ? ')
            review(f' 47 ( overall issue ) = {ans_47}')
        else:
            print('47 looks great today')

    elif server == 114:
        print('Done')
        print('it takes time to approve   ')
        time.sleep(85)
        pyautogui.click (x=473, y=375)     #  ACCEPTANCE 
        time.sleep(3)
        pyautogui.click (x=682, y=269)      # ok to approve
        time.sleep(2)
        keyboard.write('traceart@321')
        keyboard.press('enter')
        time.sleep(3)
        pyautogui.click (x=596, y=295)         #  sign in for how many days 
        time.sleep(5)
        
        eventvwr()                             # if yes , then display the event viewer for the user

        if file_explorer():
            keyboard.write(r'D:\RNLIC_Applications\SendAttachement\ErrorLogs')  # check for error log files for 114
            pyautogui.press('enter') 
            time.sleep(3)

        taskscheduler()

        ans_114 = input('was 114 ok ? ').lower()
        if ans_114  in agree:
            review('114 = no ev issue , no error log file , scheduler == ok ')
        elif ans_114 in checklist:
            print('ok then let me know , after that ill update your output to the job file ')

    elif server == 78:
        time.sleep(40)
        pyautogui.click (x=695, y=495)     # traceart@123  select ur option 
        time.sleep(3)
        keyboard.write('traceart@321')
        keyboard.press('enter')
        time.sleep(3)
        pyautogui.click (x=596, y=295)    #  sign in for how many days 
        
        eventvwr()

            
        def check_pd_logs():
            print('For PolicyDoc log files Do you ')
            if file_explorer() :                # until u type in search bar 
                keyboard.write(r'D:\TraceArt\PolicyDoc\Debug\Log\log.txt')         # checking logs for POLICY DOC
                pyautogui.press('enter') 
                time.sleep(3)
                pyautogui.click (x=631, y=302)        #click on center u check logs  so that u go back to server 
                pyautogui.click (x=1220, y=112)       # scroll  to the end of the file 
                [pyautogui.doubleClick(x=1218, y=617) for _ in range(20)]
                time.sleep(3)
                save_path=(fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\pd_log_{datetime.datetime.today().day}.jpg')
                snapshot = ImageGrab.grab()
                snapshot.save(save_path)
                print(' Done saved ur screenshot ')
                time.sleep(10)
                pyautogui.click(x=1215, y=54)   #  close the file 

                
                img = Image.open(fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\pd_log_{datetime.datetime.today().day}.jpg')
                text = tess.image_to_string(img).split()
                matches = [match for match in text if "records" in match]
                match_last_result=matches[len(matches)-1:]
                with open('job_file.txt','a')as f:
                    f.write(f'Policy doc total records for {datetime.datetime.today().day}/{datetime.datetime.today().month} = {match_last_result} \n')
                    print('Policy doc records logged ')

    
        if datetime.datetime.now().hour >= 15:                        #    after 3 pm only u can execute the policy doc command for checking the log files 
            check_pd_logs()
        else:
            print('\nnot running policy doc because its scheduled at 3 pm')
            print(f'still {14 - datetime.datetime.now().hour } hours and {60 -datetime.datetime.now().minute} minutes left to run \n')
    


        print('For whitelist and ymbot files Do you ')
        def whitelist():
            img = Image.open(fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\whitelist_{datetime.datetime.today().day}.jpg')
            text = tess.image_to_string(img).split()
            matches = [match for match in text if "@" in match]
            match_last_result=matches[len(matches)-2:]
            

            with open('job_file.txt','a')as f:
                f.write(f'\nwhitelist markup  set for {datetime.datetime.today().day}  = {match_last_result} \n')
                print('whitelist records logged ')

        if file_explorer():                     
            keyboard.write(r'D:\TraceArt\WhitlistreportforYM\Debug\reportconfig.json')         # checking markup for whitelist
            pyautogui.press('enter') 
            time.sleep(3)
            snapshot = ImageGrab.grab()
            save_path=(fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\whitelist_{datetime.datetime.today().day}.jpg')    # saving ss in ur local path 
            snapshot.save(save_path)
            print(' Done saved ur screenshot ')
            time.sleep(10)
            pyautogui.click(x=1205, y=63)                   # close the whitelist tab 
            whitelist()

            time.sleep(2)
            pyautogui.click(x=572, y=177)        # search bar
            time.sleep(2)
            keyboard.write(r'D:\TraceArt\YMBot\netcoreapp3.1\logs')                      # checking ym logs 
            pyautogui.press('enter') 
            time.sleep(2)

        taskscheduler()

        if datetime.datetime.now().isoweekday()==1 : 
            print('\n Its Monday, so going for exotell as well ')
            if file_explorer():
                keyboard.write(r'D:\TraceArt\Exotell Scheduler\Debug\log')     # open logs file 
                time.sleep(2)
                keyboard.press('enter') 
                date = input('is date correct ')
                if date not in agree:
                    pyautogui.click(x=606, y=183)             # date modified for latest date 
                
                pyautogui.doubleClick (x=452, y=234)            # checking logs for current date
                time.sleep(4)
                screenshot('exotell')
                #                   Opening the screenshot and noting the total count
                img = Image.open   (fr'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot\exotell_{datetime.datetime.today().day}.jpg')
                text = tess.image_to_string(img).split()
                matches = [match for match in text if "records" in match]
                # match_last_result=matches[len(matches)-1:]
                with open('job_file.txt','a')as f:
                    f.write(f'Exotell total records for  {datetime.datetime.today().day}/{datetime.datetime.today().month} = {matches} \n')
                    print('Exotell logged ')
                pyautogui.click (x=1206, y=59)       # close the file 



        any_review_78 =input('\n Any review to be marked for 78 ? ')
        if any_review_78 in agree:
            review(f' Errors in 78 ( overall issue ) = {any_review_78}')
        else:
            print('78 looks great today')
    
    elif server in [67,89]:
        print("\nClicking OK to confirm the server")
        if server==89:
            time.sleep(25)
            pyautogui.click (x=444, y=504)      # ok to approve
        else:
            time.sleep(65)     # 67 server
            pyautogui.click (x=470, y=379)      # ok to approve
            pyautogui.click (x=681, y=269)      # ok to approve
            time.sleep(2)
            pyautogui.doubleClick (x=716, y=282)      # click on input box
            keyboard.write(password_67)      #  server 47 password 
            keyboard.press('enter')      
            time.sleep(15)
            print('connecting to the sql server now ')
            sql_server()                           # open the sql server
            time.sleep(50)
            pyautogui.click(x=623, y=390)     # connect login to sql
            print('Making that connection ')
            time.sleep(5)
            pyautogui.hotkey('ctrl','o')
            time.sleep(2)
            pyautogui.click(x=389, y=68)     # click on search bar 
            time.sleep(2)
            pyautogui.press('space')         #  backspace
            time.sleep(2)
            pyautogui.write(r'D:\Users\rlinudge\Documents\SQL Server Management Studio')
            time.sleep(2)
            keyboard.press('enter')
            time.sleep(2)
            pyautogui.doubleClick(x=281, y=163)     # click and open common queries sql 
            time.sleep(10)
            pyautogui.click(x=1350, y=236)     # click on scrollbar   
            pyautogui.press('down', presses=150)   # scrolling down
            pyautogui.click(x=212, y=114)          # confirm db 
            time.sleep(2)
            pyautogui.write('NudgeSystem')
            keyboard.press('enter')

            rule_execution_ans = input('Did rule and entity count went correct ? \t')
            if rule_execution_ans in agree:
                review('\nrule execution and entity count went correct')
            elif rule_execution_ans in checklist:
                print('ok i"ll wait ')
            else:
                review('rule execution and entity count went wrong')

    elif server ==20:
        print('done')
        time.sleep(30)
        pyautogui.click (x=449, y=458)      # ok to approve
        time.sleep(2)
        pyautogui.click (x=686, y=496)      # ok to approve
        time.sleep(2)
        pyautogui.click (x=610, y=496)      # ok to approve
        pyautogui.click (x=650, y=510)      # ok to approve
        pyautogui.write(password_20)
        time.sleep(1)
        keyboard.press('enter')

        any_review_20 =input('\n Any review to be created for 20 | YES OR NO ? | \n? ')
        if any_review_20 in agree:
            ans_20=input('\n Tell what you want to mark ? ')
            review(f'review for 20 for ( overall issue ) = {ans_20}')
        else:
            print('20 looks great today')

    print(f'\nconnected to {server} server')

go_to_server()

hour = datetime.datetime.now().hour >=16  
min = datetime.datetime.now().minute>=30
if 16-datetime.datetime.now().hour ==0:
    print(f'\n{60-min} minutes left Now !✔ \n')
elif 16-datetime.datetime.now().hour <0:
    print('\t\tOk so now ')
else:
    print(16-datetime.datetime.now().hour,'hour and ',60 - datetime.datetime.now().minute,'minutes left to delete all the screenshots')
if hour and min:
    print('\t Deleting all the screenshots for today\n ')
    dir = r'D:\Users\tusha\Desktop\PYTHON\screenshots_by_bot'            # directory of all screenshots to be deleted at the end of the day 
    for files in os.listdir(dir):
        print(files)
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
