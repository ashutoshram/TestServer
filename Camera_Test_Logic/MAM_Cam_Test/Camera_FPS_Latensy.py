import cv2
import time


def fps_latency():
    video = cv2.VideoCapture(0)
    # set resolution to the capture frame
    video.set(3, 1920)
    video.set(4, 1080)

    video.set(5, 15)

    fps = video.get(cv2.CAP_PROP_FPS)
    print("Frames per second using video.get(cv2.CV_CAP_PROP_FPS): {0}".format(fps))

    # Number of frames to capture
    num_frames = 360

    print("Capturing {0} frames".format(num_frames))

    # rfps
    start = time.time()
    ret, frame = video.read()
    # Grab a few frames
    for i in range(1, num_frames):
        ret, frame = video.read()
        # Display the Capturing frame
        cv2.putText(frame, ('calculating fps and Latency with frame ' + str(i+1)), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow('Jabra DUT', frame)
        key = cv2.waitKey(20) & 0xFF
        # End time
    end = time.time()

    # Time elapsed
    seconds = end - start
    print("Time taken : {0} seconds".format(seconds))

    # Calculate frames per second
    fps = num_frames / seconds

    late = (seconds / num_frames)
    diff = late * 15

    latency = diff - 1
    print("Estimated frames per second : {:.2f}".format(fps))
    print("Estimated latency : {:.2f}".format(latency))
    # Release Capture Video and Return the Trace Val
    video.release()
    return fps, latency


# destroy all windowq
cv2.destroyAllWindows()
fps_latency()
