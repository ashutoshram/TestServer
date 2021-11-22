from pyzoom import ZoomClient
import time
import json
from datetime import datetime, timedelta, timezone

ZOOM_API_KEY = 'pRNWJaTbScaP-8C7Lbx23A'
ZOOM_API_SECRET = 'ebVJdL22U4viAJ6OtERaqUgcNVdtG1dAaZnK'
client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)


def meetin():
    now = datetime.now()
    local_now = now.astimezone()
    tz = local_now.tzinfo
    tzname = tz.tzname(local_now)
    print(tzname)
    dat = now.strftime('%Y/%m/%d')
    print(dat)
    rounded = now + (datetime.min - now) % timedelta(minutes=30)
    strtime = rounded.strftime('%H:%M')
    print(strtime)
    mtg_start_time = datetime.strptime(dat + ' ' + strtime, '%Y/%m/%d %H:%M')
    print(mtg_start_time)
    global prt
    crmeeting = client.meetings.create_meeting(
        'Test-Meeting', timezone=tzname, start_time=mtg_start_time.isoformat(), duration_min=30)
    mtgid = crmeeting.json()
    print(mtgid)
    prt = json.loads(mtgid)
    print(prt['id'])
    print(prt['password'])
    return prt['id'], prt['password']
def recrd():
    strrecd=client

def deltm():
    delmeet = client.meetings.delete_meeting(int(prt['id']))
    return delmeet

time.sleep(30)
