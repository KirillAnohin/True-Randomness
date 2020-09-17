from src import calibration, config
from src import vision, driving
import time
import cv2

parser = config.config()

def calibrate():
    if parser.get("Params", "Calibrate"):
        calibration.calibration()
    else:
        pass

def manual_movment():
    cv2.namedWindow("Processed")
    obj1 = driving.SerialCom()
    while True:
        k = cv2.waitKey(1)
        if k == ord("w"):
            print("WWWWWWW")
            obj1.forward(10)
        elif k == ord("s"):
            print("SSSSSSSSS")
            obj1.reverse(10)
        elif k == ord("d"):
            print("DDDDDDD")
            obj1.right(10)
        elif k == ord("a"):
            print("AAAAAAAAA")
            obj1.left(10)
        elif k == ord("p"):
            print("Break")
            break

    obj1.__del__()

    
if __name__ == "__main__":
    calibrate()
    manual_movment()

