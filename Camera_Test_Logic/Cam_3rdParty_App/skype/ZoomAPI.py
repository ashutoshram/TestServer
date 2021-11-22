

from pyzoom import ZoomClient
from datetime import datetime as dt
YOUR_ZOOM_API_KEY='qV3x_0kvTIarBf72DcNMyg'
YOUR_ZOOM_API_SECRET='JSTecmj79gLnDVVxFMPnmwGhF0hXz0IoLeFd'

client = ZoomClient(YOUR_ZOOM_API_KEY, YOUR_ZOOM_API_SECRET)

testmeet=client.meetings.create_meeting('testmeeting',start_time=dt.now().isoformat(),duration_min=30)
#meetinglist[]=client.meetings.list_meetings()

# Get all pages of meeting participants
#result_dict = client.raw.get_all_pages('/past_meetings/{meetingUUID}/participants')