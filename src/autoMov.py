from datetime import datetime
from enum import Enum, unique, auto
from typing import Tuple, Union

import cv2
import websocket
from simple_pid import PID

from src import config, vision, imageProcessing
from src.referee import Referee
from src.serialCom import serialCom


@unique
class STATE(Enum):
    EMPTYING = auto()
    WAITING = auto()
    FINDING_BALL = auto()
    DRIVING_TO_BALL = auto()
    PICKING_UP_BALL = auto()
    FINDING_BASKET = auto()
    DRIVING_TO_BASKET = auto()
    STARTING_THROWER = auto()
    THROWING_BALL = auto()


class RobotState:
    current: STATE = STATE.WAITING
    target_x: int = 0
    target_y: int = 0
    timer: Union[datetime, None] = 0

    def change_state(self, next_state):
        self.current = next_state
        self.timer = None

    def timer_ms_passed(self):
        if self.timer is None:
            self.timer = datetime.now()
        return (datetime.now() - self.timer).microseconds/1000000

    def timer_seconds_passed(self):
        if self.timer is None:
            self.timer = datetime.now()
        return (datetime.now() - self.timer).seconds


def main():
    # Class define
    state = RobotState()
    parser = config.config()
    robot = serialCom()
    image_thread = vision.imageCapRS2()
    # Socket Conn
    conn = websocket.create_connection('ws://192.168.2.66:9090/')
    ws = Referee(conn)
    # Params
    distances = []
    teamColor = "magenta"
    basketxs = []
    finaldistance = 0
    throwing = False
    counter = 0
    temp_dist_centerX = 0
    middle_px = parser.get('Cam', 'Width') / 2
    # PID
    toBallSpeed = PID(0.015, 0.00001, 0, setpoint=460)  # P=0.4 oli varem
    toBallSpeed.output_limits = (15, 75)  # Motor limits
    toBallSpeed.sample_time = 0.01
    basketCenterSpeed = PID(0.06, 0.00001, 0.003, setpoint=310)  # 0.1, 0.000001, 0.001
    basketCenterSpeed.output_limits = (-5, 5)  # Motor limits
    basketCenterSpeed.sample_time = 0.01

    while True:
        if ws.go:  # True
            teamColor = ws.basketColor
            frame = image_thread.getFrame()

            if state.current is STATE.EMPTYING:
                if robot.recive.ir == 1:
                    robot.setIr(1)
                    robot.startThrow(100)
                    robot.setServo(100)
                else:
                    if state.timer_ms_passed() > 0.5:
                        robot.setIr(0)
                        state.change_state(STATE.WAITING)
            elif state.current is STATE.WAITING:
                # waiting
                robot.setIr(0)
                robot.setServo(0)
                robot.stopThrow()
                state.change_state(STATE.FINDING_BALL)
                #
            elif state.current is STATE.FINDING_BALL:
                imageProcessing.detectLine(frame)
                ballCnts = imageProcessing.getContours(frame)
                if len(ballCnts) > 0:
                    ball_x, ball_y = imageProcessing.detectObj(frame, ballCnts)
                    print("ball_y",ball_y)
                    if ball_y > 415 and 310 < ball_x < 330:  # 30 - 60 parser.get('Cam', 'Height') - 65
                        print('found ball')
                        state.change_state(STATE.PICKING_UP_BALL)
                    else:
                        speed = max(50 - int(ball_y / 5), 20)
                        robot.omniMovement(speed, middle_px, ball_x, ball_y)
                else:
                    robot.left(10)
                #
            elif state.current is STATE.PICKING_UP_BALL:
                # picking up ball
                robot.forward(10)
                if state.timer_seconds_passed() > 1:
                    robot.stopMoving()
                    robot.setIr(0)
                    robot.setServo(50)
                    if state.timer_seconds_passed() > 8:
                        robot.setServo(-100)  # eject
                        state.change_state(STATE.FINDING_BALL)  # ball disappeared, restart
                    elif robot.recive.ir == 1:
                        state.change_state(STATE.FINDING_BASKET)
                        pass
                #
            elif state.current is STATE.FINDING_BASKET:
                # finding basket
                # to add if basket too close go back a little
                basketCnts = imageProcessing.getBasketContours(frame, teamColor)
                if len(basketCnts) > 0:
                    target_x, target_y, w, h = imageProcessing.detectObj(frame, basketCnts, False)

                    basketCenteX, basketY = target_x + w/2, target_y+h
                    distance = imageProcessing.calc_distance(w)

                    if len(distances) > 5:
                        distances.pop(0)
                        distances.append(distance)
                        finaldistance = sum(distances) / len(distances)
                    else:
                        distances.append(distance)

                    dist_from_centerX = 320
                    if target_x > -1:
                        dist_from_centerX = middle_px - basketCenteX

                    basketxs.append(dist_from_centerX)
                    print("dist_from_centerX", dist_from_centerX)

                    if 0 < dist_from_centerX < 30:
                        if (int(dist_from_centerX) == int(temp_dist_centerX)) and (dist_from_centerX != 320):
                            counter += 1
                        else:
                            temp_dist_centerX = dist_from_centerX
                            counter = 0
                    else:
                        print(-basketCenterSpeed(basketCenteX))
                        robot.rotate(-basketCenterSpeed(basketCenteX))

                    if finaldistance > 130:
                        speed = max(50 - int(basketY / 5), 20)
                        robot.omniMovement(speed, middle_px, basketCenteX, basketY)
                    elif 0 < finaldistance < 60:
                        robot.reverse(10)
                    else:
                        if counter > 3 or state.timer_seconds_passed() > 15:
                            robot.stopMoving()
                            state.change_state(STATE.DRIVING_TO_BASKET)
                            counter = 0
                else:
                    robot.left(12)
                #
            elif state.current is STATE.DRIVING_TO_BASKET:
                # driving to basket
                if state.timer_ms_passed() > 0.5:
                    state.current = STATE.STARTING_THROWER
                #
            elif state.current is STATE.STARTING_THROWER:
                # starting thrower
                throwSpeed = -0.000161064 * finaldistance**2 + 0.181854 * finaldistance + 15.205 #0.180854 ja 14.205 oli varem
                robot.startThrow(throwSpeed)
                if state.timer_ms_passed() > 0.5:
                    state.change_state(STATE.THROWING_BALL)
                #
            elif state.current is STATE.THROWING_BALL:
                # throwing ball
                robot.setIr(1)
                if state.timer_seconds_passed()+state.timer_ms_passed() > 1.5:
                    robot.setIr(0)
                    robot.setServo(0)
                    robot.startThrow(0)
                    state.change_state(STATE.FINDING_BALL)
                #
            else:
                raise Exception(f'State not implemented in main(): {state.current}')
            pass

            cv2.putText(frame, str(state.current), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1,
                        cv2.COLOR_YUV420sp2GRAY)
            cv2.imshow('Processed', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord("q"):
                break
        else:
            robot.stopMoving()
            state.change_state(STATE.EMPTYING)

    image_thread.setStopped(False)
    robot.stopThrow()
    robot.setStopped(False)
    cv2.destroyAllWindows()