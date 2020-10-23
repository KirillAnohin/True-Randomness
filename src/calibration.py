from functools import partial
import numpy as np
from src import config, vision
import cv2

parser = config.config()
kernel = np.ones((2, 2), np.uint8)


def update_range(edge, channel, filters, value):
    """
    Parameters:
        edge = "min" or "max"
        channel = 0, 1, 2 (H, S, V)
        value = new slider value
    """
    filters[edge][channel] = value


def calibrate():
    global parser

    print("Available objects: Ball, BasketBlue, BasketMagenta")
    color_name = input("Enter color name: ")

    cv2.namedWindow("Processed")
    image_thread = vision.imageCapRS2()

    try:
        filters = {
            "min": parser.get(color_name, "min"),
            "max": parser.get(color_name, "max")
        }
    except KeyError:
        filters = {
            "min": [0, 0, 0],  # HSV minimum values
            "max": [179, 255, 255]  # HSV maximum values
        }

    cv2.createTrackbar("h_min", "Processed", filters["min"][0], 179, partial(update_range, "min", 0, filters))
    cv2.createTrackbar("s_min", "Processed", filters["min"][1], 255, partial(update_range, "min", 1, filters))
    cv2.createTrackbar("v_min", "Processed", filters["min"][2], 255, partial(update_range, "min", 2, filters))
    cv2.createTrackbar("h_max", "Processed", filters["max"][0], 179, partial(update_range, "max", 0, filters))
    cv2.createTrackbar("s_max", "Processed", filters["max"][1], 255, partial(update_range, "max", 1, filters))
    cv2.createTrackbar("v_max", "Processed", filters["max"][2], 255, partial(update_range, "max", 2, filters))

    while True:
        depth_frame, frame = image_thread.getFrame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cv2.imshow("frame", frame)

        mask = cv2.inRange(hsv, tuple(filters["min"]), tuple(filters["max"]))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.medianBlur(mask, 13)

        cv2.imshow("Processed", mask)

        k = cv2.waitKey(1)
        if k == ord("q"):
            break

    for key in filters:
        parser.set(color_name, key, filters[key])
    parser.save()

    image_thread.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate()
