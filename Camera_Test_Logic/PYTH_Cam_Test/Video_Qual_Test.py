from skimage.exposure import is_low_contrast
from Camera_Test_Logic.PYTH_Cam_Test import Camera_FPS_Latensy, runningfps
import numpy as np
from numpy.linalg import norm
import imutils
import cv2
import time

global prev_frame_time
global new_frame_time


# detect Resolution
def detect_resolution(frame):
    height, width = frame.shape[0], frame.shape[1]
    resp = (str(width) + 'X' + str(height))
    cv2.putText(frame, "{}: {:}".format("Resolution", resp), (600, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return resp


# Detect Saturation
def image_colorfulness(image):
    # split the image into its respective RGB components
    (B, G, R) = cv2.split(image.astype("float"))
    # compute rg = R - G
    rg = np.absolute(R - G)
    # compute yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)
    # compute the mean and standard deviation of both `rg` and `yb`
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    # combine the mean and standard deviations
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    # derive the "colorfulness" metric and return it
    return stdRoot + (0.3 * meanRoot)


def detect_sharpness(grayscale_image, frame):
    global text, color
    fm = cv2.Laplacian(grayscale_image, cv2.CV_64F).var()
    if fm >= 600:
        text = "Sharp"
        color = (0, 255, 255)
    elif 600 > fm >= 300:
        text = "Not So Sharp"
        color = (0, 255, 0)
    else:
        text = "Not Sharp"
        color = (0, 0, 255)
    cv2.putText(frame, "{}: {:.2f}".format(text, fm), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return text, "{:.2f}".format(fm)


def detect_noise_pixalation(frame):
    s = cv2.calcHist([frame], [1], None, [256], [0, 256])
    p = 0.05
    s_perc = np.sum(s[int(p * 255):-1]) / np.prod(frame.shape[0:2])

    # Percentage threshold; above: valid image, below: noise
    s_thr = 0.5
    if s_perc > s_thr:
        text = "Noise"
        color = (0, 0, 255)
    else:
        text = "No Noise"
        color = (0, 255, 0)
    cv2.putText(frame, "{}: {:.2f}".format(text, s_perc), (300, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return text, "{:.2f}".format(s_perc)


def detect_brightness_mean_pixl(frame):
    dim = 10
    thresh = 0.40
    img = cv2.resize(frame, (dim, dim))
    # Convert color space to LAB format and extract L channel
    L, A, B = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2LAB))
    # Normalize L channel by dividing all pixel values with maximum pixel value
    L = L / np.max(L)
    # Return True if mean is greater than thresh else False
    mn = np.mean(L)
    if mn >= thresh:
        text = "High"
        color = (0, 255, 0)
    else:
        text = "low"
        color = (0, 0, 255)
    cv2.putText(frame, "{}: {:.2f}".format("Brightness-" + text, mn), (600, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return text, "{:.2f}".format(mn)


def detect_natural_brightness(frame):
    img = frame
    if len(img.shape) == 3:
        # Colored RGB or BGR (*Do Not* use HSV images with this function)
        # create brightness with euclidean norm
        brns = np.average(norm(img, axis=2)) / np.sqrt(3)

    else:
        # Grayscale
        brns = np.average(img)
    if brns < 90.00:
        text = "LOW"
        colour = (0, 0, 255)
    elif 90.00 <= brns <= 120.00:
        text = "DEFAULT"
        colour = (0, 255, 255)
    else:
        text = "HIGH"
        colour = (0, 255, 0)
    cv2.putText(frame, "{}:{:.2f}".format("Natural Brightness-" + text, brns), (600, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                colour, 2)
    return text, "{:.2f}".format(brns)


def detect_contrast(gray, edged, frame):
    # text for contrast
    text = "High"
    color = (0, 255, 0)
    # check to see if the frame is low contrast, and if so, update
    if is_low_contrast(gray, fraction_threshold=0.05, upper_percentile=99,
                       method='linear'):  # use the skimage.exposure import is_low_contrast
        text = "Low"
        color = (0, 0, 255)
    # otherwise, the frame is *not* low contrast, so we can continue
    # processing it
    else:
        """ find contours in the edge map and find the largest one,
         which we'll assume is the outline of our color correction
         card"""
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        # draw the largest contour on the frame
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)

    # draw the text on the output frame
    cv2.putText(frame, "Contrast-" + text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                color, 2)

    return text


def detect_saturation(frame):
    C = image_colorfulness(frame)
    # Displaying the Saturation level and its Value
    if C < 25.00:
        text = "Low"
        colr = (0, 0, 255)
    elif 25.00 <= C <= 40.00:
        text = "Default"
        colr = (0, 255, 255)
    else:
        text = "High"
        colr = (0, 255, 0)

    cv2.putText(frame, "{}: {:.2f}".format("Saturation" + text, C), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colr, 2)

    return text, "{:.2f}".format(C)


def get_contrastval(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    # separate channels
    L, A, B = cv2.split(lab)

    # compute minimum and maximum in 5x5 region using erode and dilate
    min = np.min(L)
    max = np.max(L)

    # convert min and max to floats
    min = min.astype(np.float64)
    max = max.astype(np.float64)

    # compute local contrast
    contrast = (max - min) / (max + min)

    # get average across whole image
    average_contrast = 100 * np.mean(contrast)

    cnstr = float(average_contrast)
    # Draw the Contrast Value
    cv2.putText(frame, "{:.2f}".format(cnstr) + "%", (200, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 255, 255), 2)
    return "{:.2f}".format(cnstr)


# grab a pointer to the input video stream
def main(fps, latency):
    global Sharpness, Noise, PixelBrightness, NaturalBrightness, Contrast, Contract_val, Saturation
    print("[INFO] accessing video stream...")
    webcam = cv2.VideoCapture(1)
    # webcam = VideoStream(src=2,framerate=30).start()
    if webcam is None:
        print("[ERROR]-No active video Stream")
    height, width = webcam.get(3), webcam.get(4)
    resolution = (height, width)
    print(resolution)
    start_time = time.time()
    duration = 60

    # loop over frames from the video stream
    while True:
        # read a frame from the video stream
        _, frame = webcam.read()
        if not _:
            print("[INFO] no frame read from stream - exiting")
            break
        # resize the frame, convert it to grayscale, blur it and then analyze

        frame = imutils.resize(frame, width=1280, height=720)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 150)

        # Detecting FPS and latency

        cv2.putText(frame, "{}{:.2f}".format("FPS:-", round(fps)), (300, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 0), 2)
        cv2.putText(frame, "{}{:.2f}".format("Latency:-", latency), (350, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        resolution = detect_resolution(frame)
        # Detect Sharpness
        Sharpness = detect_sharpness(gray, frame)
        # Detect Noise/Pixelation
        Noise = detect_noise_pixalation(frame)
        # Detect Brightness
        PixelBrightness = detect_brightness_mean_pixl(frame)
        # Detect Natural Brightness
        NaturalBrightness = detect_natural_brightness(frame)
        # Detect Contrast
        Contrast = detect_contrast(gray, edged, frame)
        Contract_val = get_contrastval(frame)
        # Detect Saturation
        Saturation = detect_saturation(frame)
        # stack the output frame and edge map next to each other
        output = np.dstack([edged] * 3)
        output = np.hstack([frame, output])
        # show the output to our screen
        cv2.imshow("Panacast-50", output)
        current_time = time.time()
        elapsed_time = current_time - start_time
        key = cv2.waitKey(27) & 0xFF
        # if elapse time reached duration set or the `q` key was pressed, break from the loop
        if elapsed_time >= duration or key == ord("q"):
            break
    webcam.release()
    cv2.destroyAllWindows()
    return {"resolution": resolution, "Sharpness": Sharpness, "Noise": Noise, "PixelBrightness": PixelBrightness,
            "NaturalBrightness": NaturalBrightness, "Contrast": Contrast, "Contrast_Val": Contract_val,
            "Saturation": Saturation}


if __name__ == "__main__":
    #fps =
    fps, latency = Camera_FPS_Latensy.fps_latency(15)
    video = main(fps, latency)
    #rfps = runningfps
    rfps=runningfps.run_fps(round(fps))

    print("Value for running FPS:{:.2f}".format(rfps))
    print(video)

    # cv2.destroyAllWindows()
