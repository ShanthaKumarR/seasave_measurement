import socket
import os
import sys

myDir = os.getcwd()
sys.path.append(myDir)


class UDP_Test_server:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 5558
        self.msg = b'expedition_name;EMB365\r\nexpedition_number;MSM80\r\nstation_name;MSM80_10\r\ntimestamp;1659343898;s\r\ndatetime;01.08.2022 08:51\r\nlatitude;-14.123456;\r\nlongitude;-76.123456;\r\ndepth;1234;m\r\nairpressure;1113.2;hPa'

        self.sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
    
        #self.start_server()
    def start_server(self):
        while True:
            self.sock.sendto(self.msg, (self.ip, self.port))
            #print(self.msg)