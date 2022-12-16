'''
 
    [*]     Marks Attendance
    [*]     Check Fits Tests 
    [*]     Confirms status of new build and its successful variants


'''

import datetime
import webbrowser
from attendance import Attendance
from vpn_connect import Connect
from find_new_builds import Builds
from Fits import Fits
from fortclient_connect import FortClientConnect

now = datetime.datetime.now()
vpn_connect = Connect('Tushar-malhan')
forclient = FortClientConnect('Tusharmalhan')
tushars_attendance = Attendance()
build = Builds();fits_tests = Fits()

MY_MAIL = "https://outlook.office.com/mail/inbox/id/AAQkAGZhN2EzMDRiLWI2OTEtNDc1MC1iOTc1LTQ1ZDljYTVjZjNjZgAQALbFIBsXDEtKlnpurnNBFyM%3D"


def run_everything():

    print('\n[*]\tRunning Your scripts\n')
    ( build.main(), fits_tests.main() ) if vpn_connect.confirmation() else \
    ( vpn_connect.run(),build.main(), fits_tests.main() )
    tushars_attendance.mark_attendance() \
    if now.weekday() != 5 and now.weekday() != 6 \
    else print('\nNot Marking attendance as Its Weekend ✌ \n')
    webbrowser.open(MY_MAIL)

run_everything()
