from collections import deque

import imutils as imutils
from pip._vendor.certifi.__main__ import args

from src import calibration, config
from src import vision, driving, imageProcessing

import cv2

parser = config.config()


def calibrate():
    if parser.get("Params", "Calibrate"):
        calibration.calibration()
    else:
        pass


def detect():
    center = None
    cv2.namedWindow("Processed")
    image_thread = vision.imageCapRS2()
    obj1 = driving.serialCom()

    while True:
        depth_frame, frame = image_thread.getFrame()
        cnts = imageProcessing.getContours(frame)
        x, y = imageProcessing.detectObj(frame, cnts)
        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1)

        if x > parser.get('Cam', 'Width')/2 + 5:
            obj1.right(4)
        elif x < parser.get('Cam', 'Width')/2 - 5:
            obj1.left(4)

        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            obj1.__del__()
            break

    cv2.destroyAllWindows()




def manual_movement():
    cv2.namedWindow("Controller")
    obj1 = driving.serialCom()
    throwSpeed = 1000
    speed = 4
    while True:
        k = cv2.waitKey(1)
        if k == ord("w"):
            print("Forward")
            obj1.forward(speed)
        elif k == ord("s"):
            print("Backward")
            obj1.reverse(speed)
        elif k == ord("d"):
            print("Right")
            obj1.right(speed)
        elif k == ord("a"):
            print("Left")
            obj1.left(speed)
        elif k == ord("t"):
            print("Throw")
            obj1.startThrow(throwSpeed)
        elif k == ord("r"):
            print("Stop throw")
            obj1.stopThrow()
        elif k == ord("p"):
            print("Break")
            obj1.__del__()
            break


if __name__ == "__main__":
    #calibrate()
    detect()
    #manual_movement()
