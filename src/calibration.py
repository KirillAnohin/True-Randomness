from functools import partial
import numpy as np
from src import config, vision
import cv2

parser = config.config()

""" 
Parameters:
    edge = "min" or "max"
    channel = 0, 1, 2 (H, S, V)
    value = new slider value
"""
def update_range(edge, channel, filters, value):
    filters[edge][channel] = value


def calibration():
    global parser

    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()

    try:
        filters = {
            "min": [parser.get("Ball_color", "Min")],
            "max": [parser.get("Ball_color", "Max")]
        }
    except Exception as e:
        print(e)
    finally:
        filters = {
            "min": [0, 0, 0],  # HSV minimum values
            "max": [179, 255, 255]  # HSV maximum values
        }

    cv2.createTrackbar("h_min", "Processed", filters["min"][0], 179, partial(calibration.update_range, "min", 0, filters))
    cv2.createTrackbar("s_min", "Processed", filters["min"][1], 255, partial(calibration.update_range, "min", 1, filters))
    cv2.createTrackbar("v_min", "Processed", filters["min"][2], 255, partial(calibration.update_range, "min", 2, filters))
    cv2.createTrackbar("h_max", "Processed", filters["max"][0], 179, partial(calibration.update_range, "max", 0, filters))
    cv2.createTrackbar("s_max", "Processed", filters["max"][1], 255, partial(calibration.update_range, "max", 1, filters))
    cv2.createTrackbar("v_max", "Processed", filters["max"][2], 255, partial(calibration.update_range, "max", 2, filters))

    while True:
        frame = image_thread.getFrame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow("frame", frame)

        mask = cv2.inRange(hsv, tuple(filters["min"]), tuple(filters["max"]))
        #mean_color = ((np.array(filters["max"]) - np.array(filters["min"])) / 2).astype(np.uint8)
        cv2.imshow("Processed", mask)

        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            break
        if k == ord("s"):
            for key in filters:
                parser.set("Ball_color", key, filters[key])
            parser.save()

    cv2.destroyAllWindows()
    image_thread.release()
