import time

from src import config
from src import vision, serialCom, imageProcessing, utils
from src import manual_movement
from simple_pid import PID

import cv2

parser = config.config()


def automotive_movement():
    cv2.namedWindow("Processed")

    throwerSpeeds = utils.readThrowerFile("../config/measurements.csv")
    image_thread = vision.imageCapRS2()
    robot = serialCom.serialCom()
    middle_px = parser.get('Cam', 'Width') / 2 - 0
    loops = 0
    ballX = -1
    basketX = -1
    basket_dist_from_centerX = 320
    min_speed = 10
    rotateForBasketSpeed = PID(0.15, 0, 0, setpoint=320)
    circling_speed = 45
    toBallSpeed = PID(0.3, 0.00001, 0.0001, setpoint=400)
    toBallSpeed.output_limits = (-50, 50)
    throwing = False
    distBuffer = []

    while True:

        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        if len(distBuffer) > 15:
            distBuffer.pop(0)

        if len(basketCnts) > 0:  # BasketCNTS
            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)

            distance = imageProcessing.calc_distance(w)
            if distance > 0:
                distBuffer.append(distance)

            print(basketX, basketY, h, w)
            if basketX > -1:
                basket_dist_from_centerX = middle_px - basketX
            else:
                basket_dist_from_centerX = 320


        if len(ballCnts) > 0:  # BallCNTS
            ballX, ballY = imageProcessing.detectObj(frame, ballCnts)

        if ballX != -1:
            if throwing:
                print(basket_dist_from_centerX)
                if 3 > basket_dist_from_centerX > -2:
                    if len(distBuffer) > 0:
                        maxdist = max(distBuffer)
                        if maxdist > 0:
                            speed = utils.throwStrength(maxdist, throwerSpeeds)
                    robot.startThrow(speed)
                    break
                    #robot.forward(40)
                    #time.sleep(10)
                    #robot.stopThrow()
                    throwing = False
                    continue

                robot.rotateAroundBall(int(-rotateForBasketSpeed(basketX)))

            elif ballY > parser.get('Cam', 'Height') - 100 and throwing == False:
                throwing = True

            else:
                robot.omniMovement(int(toBallSpeed(ballY)), middle_px, ballX, ballY)

        else:
            loops += 1
            if loops > 3:
                # diff = middle_px - ballX
                # if diff < 0:
                #     robot.right(10)
                # elif diff > 0:
                #     robot.left(10)
                robot.left(10)
                loops = 0

        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    robot.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manual_movement.manual_movement()
    else:
        automotive_movement()
