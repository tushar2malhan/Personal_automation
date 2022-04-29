
def multiple_clicks():
    import pyautogui as pt
    import time
    import datetime
    # for 5 minutes keep clicking the mouse
    # while datetime.datetime.minute < 5:
    #     pt.click(button='left')
    #     time.sleep(1)
        
    #     pt.click(pt.position())
        # click right key
        # pt.click(pt.position()[0] + 10, pt.position()[1] + 10)
        # pt.click(pt.position()[0], pt.position()[1])
        # pt.press('right') 
        # time.sleep(1)
        # if 
    from time import time, sleep
    from datetime import datetime,timedelta
    end_time = datetime.now()+timedelta(minutes=3)
    # print(end_time)
    def run_evry5Min():
        while end_time>= datetime.now():
            pt.click(pt.position())

    run_evry5Min()
    pt.hotkey('f5')
    run_evry5Min()

multiple_clicks()
