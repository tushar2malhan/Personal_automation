import time 
# import pywhatkit
import imaplib
import email
from email.header import decode_header
import re 

# import pywhatkit
import credentials as credentials
from find_new_builds import send_notification
from datetime import datetime

contact_numbers = {
    'Teenu':'+918281055652',
    'Tushar':'+917814891872',
}

def mdy_to_ymd(d):
    return datetime.strptime(d, '%d %m %y')

# account
username = credentials.all_credentials['riverbed']['email']
password = credentials.all_credentials['riverbed']['password']
imap = imaplib.IMAP4_SSL("outlook.office365.com")
imap.login(username, password)

imap.select("Inbox")

def mails_from_person(person):

    typ, data = imap.search(None, f'(FROM {person})')
    print('\n\t\t',f'MAILS FROM {person}')
    time.sleep(2)
    for num in data[0].split():
        typ, data = imap.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        print(msg['Subject'])
        print(msg['From'])
        print(msg['To'])
        print(msg['Date'])
        import pdb;pdb.set_trace()
        # msg['Date'][msg['Date'].index(',')+1:] 
        mdy_to_ymd(msg['Date'][msg['Date'].index(',')+1:msg['Date'].index('2022') +5 ].strip())
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                # test_str = body.decode('UTF-8')            
                break
        print('\n')
    return person

class Mails():

    def main(self):
        mails_from_person('AJ')
        # mails_from_person('Jigeeshu')
        
        # if counter > 6:
        #     send_notification('New mail from AJ found','Found',15)
        #     pywhatkit.sendwhatmsg(contact_numbers['tushar'], 'New mail from AJ found', 15, 15)
        # else:
        #     print(f'\n\t\tNo new mails from {person}\n')
    
        imap.close()
        imap.logout()

if __name__ == '__main__':
    tushars_mail = Mails()
    tushars_mail.main()
