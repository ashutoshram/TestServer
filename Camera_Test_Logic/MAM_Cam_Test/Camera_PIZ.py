import imutils
import cv2
import time


def camerapiz_vd():
    min_percent = 5.0
    max_percent = 10.0
    warmup = 100
    # initialize the background subtract
    fgbg = cv2.createBackgroundSubtractorMOG2()

    """initialize a boolean used to represent whether or not a given frame
    has been captured along with two integer counters -- one to count
    the total number of frames that have been captured and another to
    count the total number of frames processed"""
    captured = False
    total = 0
    frames = 0
    """open a pointer to the video file initialize the width and height of
    the frame"""
    start_time = time.time()
    duration = 60
    vs = cv2.VideoCapture(1)
    (W, H) = (None, None)
    # loop over the frames of the video

    while True:

        # grab a frame from the video
        (grabbed, frame) = vs.read()
        # if the frame is None, then we have reached the end of the video file
        if grabbed is None:
            break
        # resize the frame, and then apply the background subtractor

        frame = imutils.resize(frame, width=720)
        mask = fgbg.apply(frame)
        # apply a series of erosion and dilutions to eliminate noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # if the width and height are empty, grab the spatial dimensions
        if W is None or H is None:
            (H, W) = mask.shape[:2]
        # compute the percentage of the mask that is "foreground"
        p = (cv2.countNonZero(mask) / float(W * H)) * 100
        """if there is less than N% of the frame as "foreground" then we
        know that the motion has stopped and thus we should grab the
        frame"""

        if p < min_percent and not captured and frames > warmup:
            captured = True
            c = 0
            total += 1
            if total >= 1:
                print("[INFO] switching")
                c = total
                text = "Switch-PIZ-View"
                col = (100, 255, 0)
                cv2.putText(frame, text + "-" + str(c), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
                cv2.imshow("Captured-PIZ", frame)
            # save the  *original, high resolution* frame to disk

            print(total)
        # building the background model
        elif captured and p > max_percent:
            captured = False

        txt = "Default-PIZ-View"
        color = (0, 255, 0)
        # display the frame and detect if there is a key press
        cv2.putText(frame, txt, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Frame-TestPIZ", frame)
        cv2.imshow("Mask", mask)
        current_time = time.time()
        elapsed_time = current_time - start_time

        key = cv2.waitKey(1) & 0xFF
        # increment the frames counter
        frames += 1
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time > duration or key == ord("q"):
            break

    return total


# destroy opencv window on exit
cv2.destroyAllWindows()
camerapiz_vd()
