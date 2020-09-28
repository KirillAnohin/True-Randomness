from functools import partial
import numpy as np
from src import config, vision
import cv2

parser = config.config()
kernel = np.ones((2, 2), np.uint8)
colorSelect = 'Ball'


def update_range(edge, channel, filters, value):
    """
    Parameters:
        edge = "min" or "max"
        channel = 0, 1, 2 (H, S, V)
        value = new slider value
    """
    filters[edge][channel] = value


def calibration():
    global parser, colorSelect

    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()

    try:
        filters = {
            'Ball': {"min": parser.get("Ball", "Min"), "max": parser.get("Ball", "Max")},
            'BasketBlue': {"min": parser.get("BasketBlue", "Min"), "max": parser.get("BasketBlue", "Max")},
            'BasketMagenta': {"min": parser.get("BasketMagenta", "Min"), "max": parser.get("BasketMagenta", "Max")}
        }
    except Exception as e:
        print(e)
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

        mask = cv2.inRange(hsv, tuple(filters[colorSelect]["min"]), tuple(filters[colorSelect]["max"]))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.medianBlur(mask, 13)

        cv2.imshow("Processed", mask)

        k = cv2.waitKey(1)
        if k == ord("q"):
            image_thread.setStopped(False)
            break
        elif k == ord("n"):
            inp = input('''Please choose from Options mentioned below:
                    1. Ball
                    2. BasketBlue
                    3. BasketMagenta
                    ''')
            if int(inp) == 1:
                colorSelect = 'Ball'
            elif int(inp) == 2:
                colorSelect = 'BasketBlue'
            elif int(inp) == 3:
                colorSelect = 'BasketMagenta'
            else:
                print("Only numbers are accepted. Please select right option")

        elif k == ord("s"):
            for key in filters[colorSelect]:
                parser.set(colorSelect, key, filters[key])
            parser.save()
            print("Last changes saved")

    cv2.destroyAllWindows()
