import time
from threading import Thread
import serial

class SerialCom:
    def __init__(self, speed):
        self.speed = speed
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)


    def gs(self):
        print(self.ser.name)  # check which port was really used
        self.ser.write('gs\r\n'.encode("utf-8"))  # write a string
        vastus = ""
        vastus += self.ser.read(19).decode("utf-8")
        print(vastus)

    # sd:vasak:taga:parem
    def forward(self):
        self.ser.write(('sd:' + str(self.speed) + ':' + str(0) + ':' + str(-self.speed) + '\r\n').encode("utf-8"))

    # def back():

    # def left():

    # def right:

    def __del__(self):
        self.ser.close()
