import json
import sys
import termios
import tty

import numpy as np

from src import calibration
from functools import partial

from src import vision, driving
import cv2


def execute():
    try:
        with open("colors.json", "r") as f:
            saved_colors = json.loads(f.read())
    except FileNotFoundError:
        saved_colors = {}

    cv2.namedWindow("mask")

    print("Saved color values: ", saved_colors)
    color = input("What color to threshold: ")

    image_thread = vision.imageCapRS2()

    # Read color values from colors.json or initialize new values
    if color in saved_colors:
        filters = saved_colors[color]
    else:
        filters = {
            "min": [0, 0, 0],  # HSV minimum values
            "max": [179, 255, 255]  # HSV maximum values
        }

    cv2.createTrackbar("h_min", "mask", filters["min"][0], 179, partial(calibration.update_range, "min", 0, filters))
    cv2.createTrackbar("s_min", "mask", filters["min"][1], 255, partial(calibration.update_range, "min", 1, filters))
    cv2.createTrackbar("v_min", "mask", filters["min"][2], 255, partial(calibration.update_range, "min", 2, filters))
    cv2.createTrackbar("h_max", "mask", filters["max"][0], 179, partial(calibration.update_range, "max", 0, filters))
    cv2.createTrackbar("s_max", "mask", filters["max"][1], 255, partial(calibration.update_range, "max", 1, filters))
    cv2.createTrackbar("v_max", "mask", filters["max"][2], 255, partial(calibration.update_range, "max", 2, filters))
    width = 640
    height = 480

    while True:
        frame = image_thread.getFrame()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow("frame", frame)

        for color, filters in saved_colors.items():
            mask = cv2.inRange(hsv, tuple(filters["min"]), tuple(filters["max"]))
            #mask = cv2.bitwise_or()
            mean_color = ((np.array(filters["max"]) - np.array(filters["min"])) / 2).astype(np.uint8)
            # filtered_image[mask > 0] = mean_color
            cv2.imshow(color, mask)

        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            break
        if k == ord("s"):
            calibration.save(saved_colors, filters, color)

    cv2.destroyAllWindows()
    image_thread.release()


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


def gs():
    obj1 = driving.SerialCom(10)
    while True:
        suund = getch()
        print(suund)
        if suund == 'w':
            print("WWWWWWW")
            obj1.forward()
        elif suund == 's':
            print("SSSSSSSSS")
            obj1.reverse()
        elif suund == 'd':
            print("DDDDDDD")
            obj1.right()
        elif suund == 'a':
            print("AAAAAAAAA")
            obj1.left()
        elif suund == 'p':
            print("Break")
            break

    obj1.__del__()


if __name__ == "__main__":
    execute()
    #gs()
