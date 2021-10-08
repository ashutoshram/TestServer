import pandas as pd
import cv2
import json

url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
table = pd.read_html(url)[0]
table.columns = table.columns.droplevel()


def cam_res():
    cap = cv2.VideoCapture(2)
    resolutions = {}
    for index, row in table[["W", "H"]].iterrows():

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if height != 0.0 or width != 0.0:
            resolutions[str(width) + "x" + str(height)] = "Supported"
        else:
            resolutions[str(width) + "x" + str(height)] = "Unsupported "
    print(resolutions)
    return json.dumps(resolutions)

"""resln=cam_res()
print(resln)"""
