import cv2
import numpy as np

from src import config

parser = config.config()
kernel = np.ones((2, 2), np.uint8)

filters = {
    'Ball': {"min": parser.get("Ball", "Min"), "max": parser.get("Ball", "Max")},
    'BasketBlue': {"min": parser.get("BasketBlue", "Min"), "max": parser.get("BasketBlue", "Max")},
    'BasketMagenta': {"min": parser.get("BasketMagenta", "Min"), "max": parser.get("BasketMagenta", "Max")}
}

def detectObj(frame, cnts):
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 2:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            cv2.putText(frame, str(center), center, cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)
            cv2.putText(frame, str(round((radius ** 2) * 3.14)), (center[0] + 200, center[1]),
                        cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)
    return x, y


def getContours(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    maskBall = cv2.inRange(hsv, tuple(filters["Ball"]["min"]), tuple(filters["Ball"]["max"]))
    maskBall = cv2.morphologyEx(maskBall, cv2.MORPH_OPEN, kernel)
    maskBall = cv2.medianBlur(maskBall, 13)

    #cv2.imshow("cnts", maskBall)

    # maskBasket = cv2.inRange(hsv, tuple(basket["min"]), tuple(basket["max"]))
    # maskCombo = cv2.add(maskBall, maskBasket)

    # cv2.imshow("Processed", maskCombo)

    cnts = cv2.findContours(maskBall, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    return cnts
