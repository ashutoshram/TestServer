import cv2
import numpy as np
import subprocess
import logprint
import re
import time

# evaluate the luma for each specified brightness value, return list of results
def brightness(device, cap, ctrl, debug, log_file):
    results = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        logprint.send("\nBrightness:  {:<5}".format(c), debug, log_file)
        subprocess.call(['{} -c brightness={}'.format(device, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if time.time() > t_end and ret is True:
                break
        
        # convert to grayscale and calculate luma
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        luma = np.average(f)
        logprint.send("luma:        {:<5}".format(luma), debug, log_file)
        results.append(luma)

    return results

# evaluate otsu threshold for each contrast value, return list of results
def contrast(device, cap, ctrl, debug, log_file):
    results = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        logprint.send("\nContrast:        {:<5}".format(c), debug, log_file)
        subprocess.call(['{} -c contrast={}'.format(device, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if time.time() > t_end and ret is True:
                break
        
        # convert to grayscale and calculate otsu
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(f, 0, 255, cv2.THRESH_OTSU)
        otsu = np.average(thresh)
        logprint.send("Otsu threshold:  {}".format(otsu), debug, log_file)
        results.append(otsu)
    
    return results

# evaluate hsv for each saturation value, return list of results
def saturation(device, cap, ctrl, debug, log_file):
    results = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        logprint.send("\nsaturation:            {:<5}".format(c), debug, log_file)
        subprocess.call(['{} -c saturation={}'.format(device, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if time.time() > t_end and ret is True:
                break
        
        # convert to HSV and calculate saturation average
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        sat_avg = np.average(s)
        logprint.send("Saturation (HSV) avg:  {}".format(sat_avg), debug, log_file)
        results.append(sat_avg)
    
    return results

def sharpness(device, cap, ctrl, debug, log_file):
    results = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        logprint.send("\nsharpness:           {:<5}".format(c), debug, log_file)
        subprocess.call(['{} -c sharpness={}'.format(device, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if time.time() > t_end and ret is True:
                break
        
        # convert to grayscale and calculate lapacian variance
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(f, cv2.CV_64F).var()
        logprint.send("Laplacian variance:  {}".format(variance), debug, log_file)
        results.append(variance)
    
    return results

def white_balance(device, cap, ctrl, debug, log_file):
    results = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        logprint.send("\nwhite_balance_temperature:  {:<5}".format(c), debug, log_file)
        subprocess.call(['{} -c white_balance_temperature={}'.format(device, str(c))], shell=True)
        wb = cap.get(cv2.CAP_PROP_TEMPERATURE)
        logprint.send("White balance temperature:  {}".format(wb), debug, log_file)
        results.append(wb)
    
    return results
   