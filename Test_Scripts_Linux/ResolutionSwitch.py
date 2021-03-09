import numpy as np
import cv2
import time
import os
from datetime import date, datetime

global cap
global reboots

debug = True

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

current = date.today()
path = os.getcwd()
device_num = 0
reboots = 0

filename = "{}_resolutionfps.log".format(current)
file_path = os.path.join(path+"/resolutionfps", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"/resolutionfps"):
    os.makedirs(path+"/resolutionfps")

log_file = open(file_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

def reboot_device(cap):
    print("Panacast device error")
    os.system("sudo adb kill-server")
    os.system("sudo adb devices")
    os.system("adb reboot")
    print("Rebooting...")
    time.sleep(65)
    global device_num
    global reboots
    device_num = 0
    reboots += 1

    while True:
        cap = cv2.VideoCapture(device_num)
        if cap.isOpened():
            cap = cv2.VideoCapture(device_num)
            print("Device back online: {}\n".format(device_num))
            time.sleep(5)
            break
        else:
            device_num += 1
            time.sleep(15)


if __name__ == "__main__":
        
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        print("Device Running")
    else:
        reboot_device(cap)

    frame_count = 120
    resolution_set = [(1920, 1080), (1280,720), (1920,1080), (960, 540), (1920,1080), (640, 360), (1280, 720), (1920, 1080), (1280,720), (960, 540), (1280, 720), (640, 360), (960, 540), (1920, 1080), (960, 540), (1280, 720), (960, 540), (640, 360), (1920, 1080), (640, 360), (1280, 720)]
    #resolution_set_end = [(1920, 1080), (1280,720), (960, 540), (640, 360)]
    num_res = len(resolution_set)
    start_frame = 0
    test_frame = 0

    format_ = 'NV12'
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*format_))

    i = 1
    full_start = time.time()
    half_start = time.time()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_set[0][0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_set[0][1])
    log_print("Resolution set to %d x %d" % (resolution_set[0][0], resolution_set[0][1]))
    


    while(True):

        if start_frame == (frame_count*num_res)+frame_count-1:
            end = time.time()
            total_elapsed = end - full_start

            log_print("Test duration:          {:<5} s".format(total_elapsed))
            log_print("Total frames grabbed:   {:<5}".format(start_frame))


            fps = float((start_frame) / total_elapsed)
            log_print("Actual average fps:     {:<5}\n".format(fps))
            break

        # Capture frame-by-frame
        ret, frame = cap.read()
        start_frame += 1
        test_frame += 1
        
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if test_frame == frame_count:
            test_end = time.time()
            half_elapsed = test_end - half_start

            log_print("Test {} duration:          {:<5} s".format(i, half_elapsed))
            log_print("Total frames grabbed:   {:<5}".format(test_frame))


            fps = float((test_frame) / half_elapsed)
            log_print("Actual average fps:     {:<5}\n".format(fps))
            
            try:
                log_print("Resolution set to %d x %d" % (resolution_set[i][0], resolution_set[i][1]))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_set[i][0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_set[i][1])
            except:
                pass

            i += 1
            test_frame = 0
            half_elapsed = 0
            half_start = time.time()


    cap.release()
    cv2.destroyAllWindows()
