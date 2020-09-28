import cv2
import numpy as np

from config import config

parser = config.config()
kernel = np.ones((2, 2), np.uint8)

filters = {
    'Ball': {"min": parser.get("Ball", "Min"), "max": parser.get("Ball", "Max")},
    'BasketBlue': {"min": parser.get("BasketBlue", "Min"), "max": parser.get("BasketBlue", "Max")},
    'BasketMagenta': {"min": parser.get("BasketMagenta", "Min"), "max": parser.get("BasketMagenta", "Max")}
}


def getContours(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    maskBall = cv2.inRange(hsv, tuple(filters["Ball"]["min"]), tuple(filters["Ball"]["max"]))
    maskBall = cv2.morphologyEx(maskBall, cv2.MORPH_OPEN, kernel)
    maskBall = cv2.medianBlur(maskBall, 13)

    # maskBasket = cv2.inRange(hsv, tuple(basket["min"]), tuple(basket["max"]))
    # maskCombo = cv2.add(maskBall, maskBasket)

    # cv2.imshow("Processed", maskCombo)

    cnts = cv2.findContours(maskBall, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    return cnts
