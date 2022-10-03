import pytest
from src.seasave_measurement.server_test import UDP_Test_server
from threading import Thread
import time 
from src.seasave_measurement.Dship import Udp

class Test_Udp:
    def test_rertive_data(self):
        self.test_server = UDP_Test_server()
        server_thread = Thread(target=self.test_server.start_server, daemon=True)
        server_thread.start()
        time.sleep(2)
        data = Udp().rertive_data()
        if data:
            assert data ==['expedition_name;EMB365\r', 'expedition_number;MSM80\r', \
                'station_name;MSM80_10\r', 'timestamp;1659343898;s\r', 'datetime;01.08.2022 08:51\r', \
                    'latitude;-14.123456;\r', 'longitude;-76.123456;\r', 'depth;1234;m\r', 'airpressure;1113.2;hPa'] 
        else:
            assert data == None
               

    ''' def test_splitdata(self):
        self.test_server = UDP_Test_server()
        server_thread = Thread(target=self.test_server.start_server,daemon=True)
        server_thread.start()
        time.sleep(2)
        udp_obj = Udp()
        data = udp_obj.rertive_data()
        data = udp_obj.splitdata(data)
        
        assert udp_obj.splitdata(data) == {'airpressure': '1104.4', 'depth':'1234', 'longitude':'-76.123456', 'latitude': '-14.123456', 'time': '27.12.2021 13:06', \
         'station_name':'MSM80_10', 'expedition_name':'EMB265', 'expedition_number': 'MSM80', 'timestamp':'1640610399'}'''



