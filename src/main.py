import time

from src import config
from src import vision, serialCom, imageProcessing, utils
from src import manual_movement
from simple_pid import PID

import cv2

parser = config.config()


def automotive_movement():
    cv2.namedWindow("Processed")

    image_thread = vision.imageCapRS2()
    robot = serialCom.serialCom()

    throwerSpeeds = utils.readThrowerFile("../config/measurements.csv")
    middle_px = parser.get('Cam', 'Width') / 2
    toBallSpeed = PID(0.3, 0.00001, 0.0001, setpoint=410)
    toBallSpeed.output_limits = (-50, 50)

    iter = 0
    basket_dist_from_centerX = 320
    distBuffer = []
    throwing = False
    rotating = False
    counter = 0
    currentState = "Pause"
    circling_speed = 50

    while True:
        print("ROTATING:", rotating)
        print("THROWING:", throwing)
        depth_frame, frame = image_thread.getFrame()
        ballCnts, basketCnts = imageProcessing.getContours(frame)

        ballX = -1
        basketX = -1
        if counter > 60:
            counter = 0
            robot.stopThrow()
            robot.stopMoving()
            throwing = False

        if len(distBuffer) > 15:
            distBuffer.pop(0)

        if len(basketCnts) > 0:  # BasketCNTS
            basketX, basketY, w, h = imageProcessing.detectObj(frame, basketCnts, False)

            distance = imageProcessing.calc_distance(w)
            if distance > 0:
                distBuffer.append(distance)

            if basketX > -1:
                basket_dist_from_centerX = middle_px - basketX
            else:
                basket_dist_from_centerX = 320

        if len(ballCnts) > 0:  # BallCNTS
            ballX, ballY = imageProcessing.detectObj(frame, ballCnts)

            if ballX > -1:
                ball_dist_from_centerX = middle_px - ballX
            else:
                ball_dist_from_centerX = 320

        if throwing:
            currentState = "Throwing"
            counter += 1
            robot.forward(40)
            if counter == 1:
                if len(distBuffer) > 0:
                    maxdist = max(distBuffer)
                    if maxdist > 0:
                        speed = utils.throwStrength(maxdist, throwerSpeeds)
            robot.startThrow(speed)

        elif ballX != -1:
            cv2.putText(frame, "Ball_dist: " + str(abs(int(ball_dist_from_centerX))), (10, 370),
                        cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)
            cv2.putText(frame, "Basket_dist: " + str(abs(int(basket_dist_from_centerX))), (10, 335),
                        cv2.FONT_HERSHEY_DUPLEX, 1, cv2.COLOR_YUV420sp2GRAY)
            if rotating and not throwing:
                if abs(basket_dist_from_centerX) < 3:
                    if abs(ball_dist_from_centerX) - 18 < 46:
                        cv2.putText(frame, "Molemad on keskel! :O", (10, 470), cv2.FONT_HERSHEY_DUPLEX, 1,
                                    cv2.COLOR_YUV420sp2GRAY)
                        robot.stopMoving()
                        rotating = False
                        throwing = True
                        robot.stopThrow()
                    else:
                        currentState = "moveHorizontal"
                        min_speed = 5
                        X_speed = ball_dist_from_centerX / 20
                        if X_speed <= 0:
                            calculated_speed = -min(min_speed + abs(X_speed), 20)
                            # calculated_speed = -forward_speed
                        else:
                            calculated_speed = min(min_speed + X_speed, 20)
                        robot.moveHorizontal(calculated_speed)

                else:
                    currentState = "Rotating"
                    min_speed = 10
                    X_speed = basket_dist_from_centerX / (320 / (circling_speed - min_speed))
                    if X_speed <= 0:
                        calculated_speed = min(min_speed + abs(X_speed), circling_speed)
                    else:
                        calculated_speed = -(min(min_speed + X_speed, circling_speed))

                    robot.rotateAroundBall(calculated_speed)


            elif ballY > parser.get('Cam', 'Height') - 100 and not rotating and not throwing:
                currentState = "Close to ball, rotatig true"
                rotating = True

            else:
                currentState = "Moving to ball"
                robot.omniMovement(int(toBallSpeed(ballY)), middle_px, ballX, ballY)

        else:
            iter += 1
            if iter > 3:
                currentState = "Searching"
                robot.left(15)
                iter = 0

        cv2.putText(frame, "Olek: " + currentState, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1,
                    cv2.COLOR_YUV420sp2GRAY)
        cv2.imshow('Processed', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break

    image_thread.setStopped(False)
    robot.stopThrow()
    robot.setStopped(False)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if parser.get("Params", "manual"):
        manual_movement.manual_movement()
    else:
        automotive_movement()
