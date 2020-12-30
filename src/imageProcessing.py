import cv2
import numpy as np
from src import config

parser = config.config()
kernel = np.ones((3, 3), np.uint8)

MIN_BALL_AREA = parser.get("Params", "min_ball_area")
MIN_BASKET_AREA = parser.get("Params", "min_basket_area")

# Distance params
W = 16
F = (59 * 151) / W  # Basket laius, kaugus

filters = {
    'Ball': {"min": parser.get("Ball", "min"), "max": parser.get("Ball", "max")},
    'blue': {"min": parser.get("BasketBlue", "min"), "max": parser.get("BasketBlue", "max")},
    'magenta': {"min": parser.get("BasketMagenta", "min"), "max": parser.get("BasketMagenta", "max")}
}


def detectObj(frame, cnts, isBall=True):
    c = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(c)

    if isBall:
        if area < MIN_BALL_AREA:
            return -1, -1
        else:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)

            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # only proceed if the radius meets a minimum size
                if radius > 3:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    cv2.putText(frame, str(center), center, cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)
                    cv2.putText(frame, str(round((radius ** 2) * 3.14)), (center[0] + 200, center[1]),
                                cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)

            return x, y

    else:
        if area < MIN_BASKET_AREA:
            return -1, -1, -1, -1
        else:
            M = cv2.moments(c)
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            (x, y, w, h) = cv2.boundingRect(c)
            # print("Basket size: ", w*h)
            # print("wh " + str(w*h))
            if h >= 5 and (w * h >= 800):
                print(w*h)
                cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
                cv2.putText(frame, "Laius: " + str(round(w)), (10, 300), cv2.FONT_HERSHEY_DUPLEX, 1,
                            cv2.COLOR_YUV420sp2GRAY)
                return x, y, w, h
            else:
                return -1, -1, -1, -1


def calc_distance(width):
    distance = round((W * F) / width, 2)
    return distance

def getContours(frame, teamColor):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # maskBall = cv2.medianBlur(hsv, 7)

    maskBall = cv2.inRange(hsv, tuple(filters["Ball"]["min"]), tuple(filters["Ball"]["max"]))
    maskBall = cv2.morphologyEx(maskBall, cv2.MORPH_OPEN, kernel)
    maskBall = cv2.dilate(maskBall, kernel, iterations=2)

    maskBasket = cv2.inRange(hsv, tuple(filters[teamColor]["min"]), tuple(filters[teamColor]["max"]))
    maskBasket = cv2.morphologyEx(maskBasket, cv2.MORPH_OPEN, kernel)
    #maskBasket = cv2.morphologyEx(maskBasket, cv2.MORPH_OPEN, kernel)
    maskBasket = cv2.dilate(maskBasket, kernel, iterations=2)

    maskCombo = cv2.add(maskBall, maskBasket)

    cv2.imshow("Processed", maskCombo)

    ballcnts = cv2.findContours(maskBall, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    basketcnts = cv2.findContours(maskBasket, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    return ballcnts, basketcnts
