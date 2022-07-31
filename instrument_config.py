import subprocess
from dataclasses import dataclass
from abc import ABC, abstractmethod
from xml.dom import minidom 
from typing import Callable
import glob
import os

class DataStructuringStrategy(ABC):
    @abstractmethod
    def generate_structured_data(self, instrument_config_file:str, output_folder_path:str, setup_file_path:str)->dict:
        pass

@dataclass
class Pressure(ABC):
    @abstractmethod
    def create_New_pressure_tags(self):
        """ Removes and creates new pressure tag with respect to the number of bottles """

    @abstractmethod
    def set_pressure_value(self):
        """ writes the pressure value to the system file """

class Seasave(ABC):
    @abstractmethod
    def start_seasave_auto_firing(self)->None:
        """To start the seasave application"""

class MetaDataWriter(ABC):

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create_new_prompt_tag(self):
        """To remove and create new prompt tag"""
    
    @abstractmethod
    def set_meta_data(self):
        """ To write metadata to the sysstem file"""

class Water_sampler(ABC):
    @abstractmethod
    def firing_mode(self):
        pass

class IOWWaterSampler(Water_sampler):
    @staticmethod
    def firing_mode( mode:int = None)->str:
        if mode == 1:
            return str(0)
        elif mode == 2:
            return str(3)
        else:
            return str(0)

class DataDictionary(DataStructuringStrategy):
    @staticmethod   
    def generate_structured_data(water_sampler_option = 0, instrument_config_file:str = None, output_folder_path:str = None, setup_file_path:str = None, firing_mode:str = None):

        data_dict = {'ConfigurationFilePath':{'value':instrument_config_file}, 'DataFilePath':{'value': output_folder_path},\
            'SetupFilePath':{'value': setup_file_path}, 'WaterSamplerConfiguration': [{'FiringSequence': firing_mode}, {'Type': water_sampler_option}]}      
        return data_dict



def SBE_carosusel_type(type:str)->int:
    if type == 'SBE_carosuel':
        return 5

class ComputeLastFileName(ABC):
    @abstractmethod
    def get_last_file_name()->str:
        '''to compute the last file name '''

class ComputeLastOutputFileName(ComputeLastFileName):
    @staticmethod
    def get_last_file_name(output_data_folder)->str:
        list_of_files = glob.glob(output_data_folder+'\\*.hex') # * means all if need specific format then *.csv
        try:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file.split('\\')[-1] 
        except ValueError:
            return 'No previous record found'

class GetPathValues:
    def __init__(self, instrument_confi_file:str = None , setup_file_path:str = None , output_folder_path:str = None, \
        data_structure_type:DataStructuringStrategy = None , bottle_firing_mode:int =0):
        
        self.instrument_confi_file = instrument_confi_file
        self.setup_file_path = setup_file_path
        self.output_folder_path = output_folder_path
        self.data_structure_type = data_structure_type
        self.bottle_firing_mode = bottle_firing_mode
   
    def structuring_the_data(self, output_file_name, water_sampler_option, bottle_firing_type:Callable[[IOWWaterSampler], None] = None)->dict:
        return self.data_structure_type.generate_structured_data(water_sampler_option, self.instrument_confi_file, self.generate_output_file_path(output_file_name), self.setup_file_path, \
                bottle_firing_type.firing_mode(self.bottle_firing_mode))


    def write_file_path(self, path_data:dict)->None:      
        for key, _ in  path_data.items():
            if key != 'WaterSamplerConfiguration':
                with open(path_data['SetupFilePath']['value'], 'r') as tags:
                    domObj = minidom.parse(tags)
                    group = domObj.documentElement
                    Cookie = group.getElementsByTagName(key)
                    Cookie[0].setAttribute('value', path_data[key]['value'])
                    with open(path_data['SetupFilePath']['value'], 'w') as tags:
                        domObj.writexml(tags)
                   
            else:
                for d in path_data[key]:
                    for new_key, _ in d.items():
                        with open(path_data['SetupFilePath']['value'], 'r') as tags:
                            domObj = minidom.parse(tags)
                            group = domObj.documentElement
                            Cookie = group.getElementsByTagName(key)
                            
                            Cookie[0].setAttribute(new_key, d[new_key])
                            with open(path_data['SetupFilePath']['value'], 'w') as tags:
                                domObj.writexml(tags)
        
    def generate_output_file_path(self, output_file_name):
        return self.output_folder_path+'\\'+output_file_name

    

class SetPressure(Pressure):
    def __init__(self, setup_file_path:str = None):
        self.setup_file_path = setup_file_path
        
    def create_New_pressure_tags(self, num_bottles:int = None)->None:
        from xml.parsers.expat import ExpatError
        try:
            with open(self.setup_file_path,'r') as f:
                xmldoc = minidom.parse(f)   
                Data = xmldoc.getElementsByTagName('WaterSamplerConfiguration')[0]
                Data.setAttribute("NumberOfWaterBottles", str(num_bottles))
                AutoFireData = Data.getElementsByTagName('AutoFireData')[0]
                DataTable = AutoFireData.getElementsByTagName('DataTable')            
                for i in DataTable:
                    RmRow = i.getElementsByTagName('Row')
                [j.parentNode.removeChild(j) for j in RmRow]
                for indx, botnum in enumerate(range(1, num_bottles+1)):
                    newRow = xmldoc.getElementsByTagName('DataTable')[0].appendChild(xmldoc.createElement("Row"))        
                    newRow.setAttribute("BottleNumber",str(botnum))          
                    newRow.setAttribute("index", str(indx))
                    newRow.setAttribute("FireAt", str(-0)) 
            with open(self.setup_file_path, 'w', newline='') as f:
                xmldoc.writexml(f)
        except FileNotFoundError:
            print('File not found')
        except ExpatError:
            print('file is empty')

    def set_pressure_value(self, pressure_value: list = None):
        try:          
            print('The pressure value is ', pressure_value) 
            with open(self.setup_file_path,'r') as f:    
                xmldoc = minidom.parse(f)        
                Data = xmldoc.getElementsByTagName('WaterSamplerConfiguration')[0]
                AutoFireData = Data.getElementsByTagName('AutoFireData')[0]
                DataTable = AutoFireData.getElementsByTagName('DataTable')               
                for i in DataTable:
                    RmRow = i.getElementsByTagName('Row')
                    for inx, row_tags in enumerate(RmRow):
                        RmRow[inx].setAttribute("BottleNumber", str(inx+1))
                        RmRow[inx].setAttribute("index", str(inx))
                        RmRow[inx].setAttribute("FireAt", str(pressure_value[inx]).replace(',', '.'))
                with open(self.setup_file_path, 'w', newline='') as f:
                    xmldoc.writexml(f)
        except  FileNotFoundError:
            print('No file found in the given location')

class MetaDataWriter:
    def __init__(self, setup_file_name, meta_data_dict):
        self.setup_file_path = setup_file_name
        self.meta_data_dict = meta_data_dict
        try:
            self.create_new_prompt_tag()
            self.set_mata_data()
        except:
            print('Problem in collecting Meta data for the GUI ')
    def create_new_prompt_tag(self):
        try:
            with open(self.setup_file_path,'r') as f:
                xmldoc = minidom.parse(f)        
                HeaderForm = xmldoc.getElementsByTagName('HeaderForm')

                for header in HeaderForm:
                    prmt = header.getElementsByTagName('Prompt')
                [j.parentNode.removeChild(j) for j in prmt]

                for indx, _ in enumerate(range(1, len(self.meta_data_dict)+1)):
                    newRow = xmldoc.getElementsByTagName('HeaderForm')[0].appendChild(xmldoc.createElement("Prompt"))                
                    newRow.setAttribute("index", str(indx))
            with open(self.setup_file_path, 'w') as f:               
                    xmldoc.writexml(f)
        except FileNotFoundError:
            print('file is missing')

    def set_mata_data(self):
        try:          
            with open(self.setup_file_path,'r') as f:    
                xmldoc = minidom.parse(f)        
                Data = xmldoc.getElementsByTagName('HeaderForm')         
                for i in Data:
                    RmRow = i.getElementsByTagName('Prompt')
                    for inx, key in zip (enumerate(RmRow), self.meta_data_dict):
                        RmRow[inx[0]].setAttribute("value", key+' = '+ str(self.meta_data_dict[key]))
                with open(self.setup_file_path, 'w', newline='') as f:
                    xmldoc.writexml(f)
        except  FileNotFoundError:
            print('No file found in the given location')


class StartSeaSave:
    def __init__(self, setup_file_name = None):
        self.setup_file_name = setup_file_name

    '''def start_seasave_auto_firing(self, seasave_executable_path)->None:
            secargs = [seasave_executable_path, self.setup_file_name, '-autofireondowncast']
            p =subprocess.Popen(secargs)'''


