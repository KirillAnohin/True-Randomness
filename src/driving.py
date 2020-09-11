import time
from threading import Thread
import serial

class SerialCom:
    def __init__(self, speed):
        self.vastus = ""
        self.speed = speed
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
        print(self.ser.name)


    def gs(self):
        self.ser.write('gs\r\n'.encode("utf-8"))
        self.vastus += self.ser.read(19).decode("utf-8")
        print(self.vastus)

    # sd:vasak:taga:parem
    def forward(self):
        self.ser.write(('sd:' + str(self.speed) + ':' + str(0) + ':' + str(-self.speed) + '\r\n').encode("utf-8"))

    def reverse(self):
        self.ser.write(('sd:' + str(-self.speed) + ':' + str(0) + ':' + str(self.speed) + '\r\n').encode("utf-8"))

    def left(self):
        self.ser.write(('sd:' + str(-self.speed) + ':' + str(-self.speed) + ':' + str(-self.speed) + '\r\n').encode("utf-8"))

    def right(self):
        self.ser.write(('sd:' + str(self.speed) + ':' + str(self.speed) + ':' + str(self.speed) + '\r\n').encode("utf-8"))

    def __del__(self):
        self.ser.close()
