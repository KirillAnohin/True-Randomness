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
            obj1.__del__()
            print("Break")
            break

def conture():

    cv2.namedWindow("Processed")
    image_thread = vision.imageCapRS2()

    while True:
        depth_frame, frame = image_thread.getFrame()

        bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)

        edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

        cv2.imshow('Edge', edge_detected_image)

        contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contour_list = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(contour)
            if (len(approx) > 8) & (len(approx) < 23):
                contour_list.append(contour)

        cv2.drawContours(frame, contour_list, -1, (255, 0, 0), 2)

        cv2.imshow('Processed', frame)

        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate()
    #manual_movment()
    #conture()


