import math
import struct
import threading
import time

import serial
from dataclasses import dataclass

import config


@dataclass
class Command:
    motor1: float = 0
    motor2: float = 0
    motor3: float = 0
    thrower: float = 0
    servo: float = 0
    ir: int = 0
    # pGain: float = 0
    # iGain: float = 0
    # dGain: float = 0
    pid_type: int = 0  # 0 = instant pid; 1 = avg of last 10 values
    delimiter: int = 0xABCABC
    # format = 'fffiiifffii'
    format = 'fffffiii'
    size = struct.calcsize(format)

    def pack(self):
        return struct.pack(
            self.format,
            self.motor1,
            self.motor2,
            self.motor3,
            self.thrower,
            self.servo,
            self.ir,
            # self.pGain,
            # self.iGain,
            # self.dGain,
            self.pid_type,
            self.delimiter)

    def unpack(self, packed):
        unpacked = struct.unpack(self.format, packed)
        self.motor1 = unpacked[0]
        self.motor2 = unpacked[1]
        self.motor3 = unpacked[2]
        self.thrower = unpacked[3]
        self.servo = unpacked[4]
        self.ir = unpacked[5]


class serialCom:

    def commandThread(self):
        while self.running:
            self.command.motor1 = float(self.speed[1]) #keskmine
            self.command.motor2 = float(self.speed[2]) #vasak
            self.command.motor3 = float(self.speed[0]) #parem
            self.command.thrower = int(self.throwSpeed)
            self.command.servo = int(self.servo)
            self.command.ir = int(self.ir)

            #print(f'm1:{self.command.motor1} m2:{self.command.motor2} m3:{self.command.motor3}')
            #print(f'send:{self.command.ir} recive:{self.recive.ir}')

            drive = self.command.pack()

            time.sleep(0.002)
            self.ser.write(drive)

            while self.ser.inWaiting() > 0:
                data = self.ser.read(self.recive.size)
                self.recive.unpack(data)
                #self.ir = self.recive.ir
                #print(f'r1:{self.recive.motor1} r2:{self.recive.motor2} r3:{self.recive.motor3}')

    def __init__(self):
        # Params
        self.command = Command()
        self.recive = Command()
        self.throwSpeed, self.speed, self.servo = 0, [0, 0, 0], 0
        self.ir = 0
        self.middle_wheel_angle = 0
        self.forward_movement_angle = 90
        self.right_wheel_angle = 120
        self.left_wheel_angle = 240
        # Parser define
        self.parser = config.config()
        # WebSocket params
        self.gameStatus = False
        self.baskets = "magenta"
        self.robotID = self.parser.get("Game", "robotID")
        # Connection to websocket

        # Serial connection
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
        print(self.ser.name)
        # Thread
        self.running = True
        self.w = threading.Thread(name='commandThread', target=self.commandThread)
        self.w.start()

    # sd:right:middle:left
    def forward(self, speed):
        self.speed = [speed, 0, -speed]

    def reverse(self, speed):
        self.speed = [-speed, 0, speed]

    def left(self, speed):
        self.speed = [speed, -speed, speed]

    def right(self, speed):
        self.speed = [-speed, speed, -speed]

    def move(self, speed):
        self.speed = [speed[0], speed[1], speed[2]]

    def startThrow(self, speed):
        self.throwSpeed = speed

    def setServo(self, speed):
        self.servo = speed

    def setIr(self, state):
        self.ir = state

    def stopThrow(self):
        self.throwSpeed = 0

    def stopMoving(self):
        self.speed = [0, 0, 0]

    def rotate(self, speed):
        self.speed = [-speed, speed, -speed]

    def calcDirectionAngle(self, robotDirectionAngle, middle_px, X, Y):
        try:
            robotDirectionAngle = int(math.degrees(math.atan((middle_px - X) / Y)) + robotDirectionAngle)
        except ZeroDivisionError:
            robotDirectionAngle = 0.1
        return robotDirectionAngle

    def wheelLinearVelocity(self, robotSpeed, wheelAngle, robotDirectionAngle, middle_px=None, X=None, Y=None):
        if Y is not None and Y != 0:
            robotDirectionAngle = self.calcDirectionAngle(robotDirectionAngle, middle_px, X, Y)
            wheelLinearVelocity = robotSpeed * math.cos(math.radians(robotDirectionAngle - wheelAngle))
        else:
            wheelLinearVelocity = robotSpeed * math.cos(math.radians(robotDirectionAngle - wheelAngle))
        return wheelLinearVelocity

    # sd:right:middle:left
    def omniMovement(self, speed, middle_px, X=None, Y=None):
        self.speed[0] = int(
            self.wheelLinearVelocity(speed, self.right_wheel_angle, self.forward_movement_angle, middle_px, X, Y))
        self.speed[1] = int(
            self.wheelLinearVelocity(speed, self.middle_wheel_angle, self.forward_movement_angle, middle_px, X, Y))
        self.speed[2] = int(
            self.wheelLinearVelocity(speed, self.left_wheel_angle, self.forward_movement_angle, middle_px, X, Y))

    def setStopped(self, stopped):
        self.running = stopped
        self.speed, servo, throwSpeed = [0, 0, 0], 0, 0
        time.sleep(0.2)
        self.ser.close()
