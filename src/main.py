from collections import deque
from pip._vendor.certifi.__main__ import args

from src import calibration, config
from src import vision, driving, imageProcessing

import cv2

parser = config.config()


def detect():
    cv2.namedWindow("Processed")
    image_thread = vision.imageCapRS2()
    obj1 = driving.serialCom()

    while True:
        depth_frame, frame = image_thread.getFrame()
        cnts = imageProcessing.getContours(frame)
        cv2.imshow('Processed', frame)
        if len(cnts) > 0:
            x, y = imageProcessing.detectObj(frame, cnts)
            if x > 210 and x < 480 :
                obj1.move([0,0,0])
            elif x > parser.get('Cam', 'Width') / 2 + 30:
                obj1.right(4)
            elif x < parser.get('Cam', 'Width') / 2 - 30:
                obj1.left(4)
        else:
            obj1.left(4)
        k = cv2.waitKey(1)
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    obj1.setStopped(False)
    cv2.destroyAllWindows()


def manual_movement():
    cv2.namedWindow("Controller")
    obj1 = driving.serialCom()
    throwSpeed = 200
    speed = 10
    while True:
        k = cv2.waitKey(1)
        if k == ord("w"):
            print("Forward")
            obj1.moveVertical(speed)
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
        elif k == ord("q"):
            print("Break")
            break

    obj1.setStopped(False)


if __name__ == "__main__":
    #detect()
    manual_movement()
