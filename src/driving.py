import threading
import time
from threading import Thread
import serial


class SerialCom:

    def commandThread(self):
        while self.running:
            text = ("sd:" + str(self.speed[0]) + ":" + str(self.speed[1]) + ":" + str(self.speed[2]) + "\r\n")
            time.sleep(0.05)
            print(self.speed)
            self.ser.write(text.encode("utf-8"))
            while self.ser.inWaiting() > 0:
                self.ser.read()

    def __init__(self):
        self.running = True
        self.speed = [0, 0, 0]
        self.w = threading.Thread(name='commandThread', target=self.commandThread)
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
        print(self.ser.name)
        self.w.start()

    def gs(self):
        self.ser.write('gs\r\n'.encode("utf-8"))
        response = self.ser.read(20).decode("utf-8")
        return response

    # sd:vasak:taga:parem
    def forward(self, speed):
        self.speed = [speed, 0, -speed]

    def reverse(self, speed):
        self.speed = [-speed, 0, speed]

    def left(self, speed):
        self.speed = [-speed, -speed, -speed]

    def right(self, speed):
        self.speed = [speed, speed, speed]

    def __del__(self):
        self.running = False
        self.speed = [0, 0, 0]
        self.ser.close()
