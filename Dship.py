import json
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import io
import socket


class Dship:
    @staticmethod
    def key_value_seperation(file_name = 'measurement\\info_files\\meta_data_info.json'):
        with open(file_name, 'r') as dict_obj:
            info = json.load(dict_obj)
        keys = [i for i in  info ]
        url_List = [info[i] for i in info]
        return keys, url_List

    @staticmethod
    def retrive_data(keys, url_List)->dict:
        data_dict = {} 
        for key in keys:
            data_dict[key] = 'Data loading'  
        for key, url in zip(keys, url_List):
            try:
                page = urlopen(url = url, timeout=1)
                html_bytes = page.read()
                html = html_bytes.decode("utf-8")
                f = io.StringIO(html)   
                mytree = ET.parse(f)                       
                myroot = mytree.getroot()
                data_dict[key] = myroot[0].text    
                #yield data_dict                        
            except:
                data_dict[key] = 'Error' 
                #yield data_dict
        return data_dict
    
class Udp:
    def __init__(self):     
        self.udp_running = True
        self.port = 5558
        self.ip = socket.gethostbyname(socket.gethostname())
        #print(self.ip)
        #self.ip = "10.242.2.2"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.data_dict = dict()
        self.sock.settimeout(2.0)

    def rertive_data(self):
        try:
            data, self.addr = self.sock.recvfrom(1024) 
            data = data.decode('utf-8')
            #print(data)
            return  data.split('\n')
        except socket.timeout:
            return  None

    def splitdata(self, data_split):    
        meta_data_dict = {'airpressure': 'udp error', 'depth':'udp error', 'longitude':'udp error', 'latitude': 'udp error', 'time': 'udp error', \
            'station_name':'udp error', 'expedition_name':'udp error', 'expedition_number': 'udp error', 'timestamp':'udp error'}  
        if data_split != None:
                for inx, val in zip(enumerate(range(len(data_split))), list(meta_data_dict.keys())):
                    try:
                        if data_split[inx[0]].split(';')[0].split()[0] == 'datetime':
                           
                            meta_data_dict[data_split[inx[0]].split(';')[0].split()[0]] = data_split[inx[0]].split(';')[1].split()[1]
                        else:
                            meta_data_dict[data_split[inx[0]].split(';')[0].split()[0]] = data_split[inx[0]].split(';')[1].split()[0]
                    except:
                        meta_data_dict[data_split[inx[0]].split(';')[0].split()[0]] = 'Data_missing'
                return meta_data_dict
        else:
            return meta_data_dict