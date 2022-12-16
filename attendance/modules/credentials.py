from pathlib import Path

all_credentials = {
    "globalProtect": {
        'email_id':'jjjanardhanan@riverbed.com',
        'username': 'jjjanardhanan',
        'password': 'strange@2022Q1' ,
    },
    'servers': {
        'common_password':'2top90!'
    },
    'outlook':{
        'username':'tushar.m',
        'email_id':'tushar.m@Thinkpalm.com',
    },
    'fortclient':{
        'username':'tushar.m',
        'password':'ThinkVpN@#13',
    },
    'attendance':{
        'username':'tushar.m',
        'password':'Dec#22',     # Domain password ~ jira ( Atlassian ), Heads, Tcube
    },
    'cpdss':{
        'email':'tushar.m@alphaori.sg',
        'password':'tusharmalhan@1',
    },

    'riverbed':{
        'email':'tmalhan@riverbed.com',
        'id':'tmalhan',
        'password':'Oauth@2022Q4',   # AD, UNIX same pass
    },
    'driver_path':str(Path.home()/"Downloads/chromedriver_win32/chromedriver.exe"),
    'pics_dir':str(Path.home()/"Desktop/attendance/pics")
    
}
