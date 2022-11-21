import datetime
def cleanWeekNo(yr, mth, date):
    curr_wk_no = datetime.date(yr,mth,date).isocalendar()[1]
    if (mth == 1) & (curr_wk_no > 50):
        wk_no = 1
    elif (mth == 12) & ((curr_wk_no < 3)| (curr_wk_no == 53)):
        wk_no = 52
    else:
        wk_no = curr_wk_no
    return wk_no

def avgResults(results):
    if results is None:
        return None
    else:
        arr = extractColumn(results)
        avg = sum(arr)/len(arr)
        return arr, avg

def extractColumn(results):
    return list(map(lambda x:x[0], results))

def uniqueCargo(arr):
    cleanArr = extractColumn(arr)
    result = list(set(cleanArr))
    result.sort()
    return result