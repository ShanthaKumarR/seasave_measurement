import os
from pickle import NONE 
from xml.dom import minidom 
import pytest
from instrument_config import IOWWaterSampler
from instrument_config import SBE_carosusel_type, ComputeLastOutputFileName, SetPressure, MetaDataWriter, scanfish_water_sampler_type
import shutil
import time

class Test_DataDictionary:
    
    @pytest.mark.parametrize('water_sampler_option, instrument_config_file, output_folder_path, setup_file_path, firing_mode', [(0, None, None, None,  None)])
    def test_generate_structured_data(self,water_sampler_option, instrument_config_file, output_folder_path, setup_file_path, firing_mode,  DataDictionary_obj):
        data = DataDictionary_obj.generate_structured_data(water_sampler_option,instrument_config_file, output_folder_path, setup_file_path, firing_mode)
        #check the main key
        main_keys = ['ConfigurationFilePath', 'DataFilePath','SetupFilePath', 'WaterSamplerConfiguration']
        #check values
        for key, main_key in zip(data, main_keys):
            assert key == main_key
            if key == 'ConfigurationFilePath':
                assert data[key]['value'] == instrument_config_file
            elif key == 'DataFilePath':
                assert data[key]['value'] == output_folder_path
            elif key == 'WaterSamplerConfiguration':
                for i in data[key]:
                    if i == 'water_sampler_option':
                        assert i['water_sampler_option'] == water_sampler_option
                    elif i == 'firing_mode':
                        assert i['firing_mode'] == firing_mode
            elif key == 'setup_file_path':
                assert data[key]['value'] == setup_file_path
        #check type
        assert type(DataDictionary_obj.generate_structured_data(water_sampler_option,instrument_config_file, output_folder_path, setup_file_path, firing_mode )) == dict
        

class Test_GetPathValues:

    def test__init__(self, get_path_values_object_init):
        member_variable_dict ={'k_1':get_path_values_object_init.instrument_confi_file, 'k_2': get_path_values_object_init.setup_file_path,\
            'key_3':get_path_values_object_init.output_folder_path, 'k_3': get_path_values_object_init.data_structure_type, \
                'k_4': get_path_values_object_init.bottle_firing_mode}
        try: 
            for key in member_variable_dict:
                if member_variable_dict[key] == None:
                    assert True
                else:
                    assert False
        except AssertionError:
            if member_variable_dict[key] ==0:
                assert True
            else:
                assert False
    
    @pytest.mark.parametrize('output_file_name, water_sampler_option, bottle_firing_type',[('CTD_station_name_cast_number', str(5), IOWWaterSampler)] )
    def test_structuring_the_data(self, get_path_values_object, output_file_name, water_sampler_option, bottle_firing_type):
        data = get_path_values_object.structuring_the_data(water_sampler_option, output_file_name,bottle_firing_type)
        assert type(data) == dict

    @pytest.mark.parametrize('output_file_name, water_sampler_option, bottle_firing_type',[('CTD_station_name_cast_number', str(6), IOWWaterSampler)] )
    def test_write_file_path(self, get_path_values_object, output_file_name, water_sampler_option, bottle_firing_type):
        path_data = get_path_values_object.structuring_the_data(output_file_name, water_sampler_option, bottle_firing_type)
    
        get_path_values_object.write_file_path(path_data)
        
        for key, _ in  path_data.items():
            if key != 'WaterSamplerConfiguration':
                with open(path_data['SetupFilePath']['value'], 'r') as tags:
                    domObj = minidom.parse(tags)
                    group = domObj.documentElement
                    Cookie = group.getElementsByTagName(key)
                    assert Cookie[0].getAttribute('value') == path_data[key]['value']
            else:
                for d in path_data[key]:
                    for new_key, _ in d.items():
                        with open(path_data['SetupFilePath']['value'], 'r') as tags:
                            domObj = minidom.parse(tags)
                            group = domObj.documentElement
                            Cookie = group.getElementsByTagName(key) 
                            assert Cookie[0].getAttribute(new_key) == d[new_key]



class Test_IOWWaterSampler:
    @pytest.mark.parametrize(('mode', 'expected'), ((1, '0'), (2,'3'), (NONE, '0')))
    def test_firing_mode(self, mode, expected):
        assert IOWWaterSampler.firing_mode(mode) == expected


def test_SBE_carosusel_type():
    assert SBE_carosusel_type() == 5

def test_scanfish_water_sampler_type()->int:
    assert scanfish_water_sampler_type() ==0

class Test_ComputeLastOutputFileName:
    def test_get_last_file_name_norecord(self):
        try:
            os.mkdir('temp')
            assert ComputeLastOutputFileName.get_last_file_name('temp') == 'No previous record found'
            os.rmdir('temp')
        except FileExistsError:
            assert ComputeLastOutputFileName.get_last_file_name('temp') == '02.hex'
            shutil.rmtree('temp')
    
    def test_get_last_file_name_with_record(self):
        try:
            os.mkdir('temp')
            test_file_list = ['01.hex', '02.hex']
            for file_name in test_file_list:
                with open('temp\\'+file_name, 'w') as file:
                    print('Creating :', 'temp\\'+file_name)
                    time.sleep(2)  
            assert ComputeLastOutputFileName.get_last_file_name('temp') == '02.hex'
            shutil.rmtree('temp')
        except FileExistsError:
            assert ComputeLastOutputFileName.get_last_file_name('temp') == '02.hex'
            shutil.rmtree('temp')


class Test_SetPressure:
    @pytest.mark.parametrize(('num_bottles', 'expected'), ((5, 5), (2,2), (3, 3)))
    def test_create_New_pressure_tags(self, SetPressure_obj, num_bottles, expected):

        SetPressure_obj.create_New_pressure_tags(num_bottles)
        with open(SetPressure_obj.setup_file_path,'r') as f:
            xmldoc = minidom.parse(f)   
            Data = xmldoc.getElementsByTagName('WaterSamplerConfiguration')[0]
            AutoFireData = Data.getElementsByTagName('AutoFireData')[0]
            DataTable = AutoFireData.getElementsByTagName('DataTable') 
            for i in DataTable:
                RmRow = i.getElementsByTagName('Row')
            assert len(RmRow) == expected
            for (indx, botnum), newRow in zip(enumerate(range(1, num_bottles+1)), DataTable):       
                assert  newRow.getElementsByTagName('Row')[0].getAttribute("BottleNumber") == str(botnum)         
                assert newRow.getElementsByTagName('Row')[0].getAttribute("index")== str(indx)
                assert  newRow.getElementsByTagName('Row')[0].getAttribute("FireAt")== str(-0)

    @pytest.mark.parametrize("pressure_value, bottle_number", [([5,6] ,2), ([2, 3, 4, 5], 4)])
    def test_set_pressure_value(self, SetPressure_obj, pressure_value, bottle_number):
        SetPressure_obj.create_New_pressure_tags(bottle_number)
        SetPressure_obj.set_pressure_value(pressure_value)
        with open(SetPressure_obj.setup_file_path,'r') as f:    
                    xmldoc = minidom.parse(f)        
                    Data = xmldoc.getElementsByTagName('WaterSamplerConfiguration')[0]
                    AutoFireData = Data.getElementsByTagName('AutoFireData')[0]
                    DataTable = AutoFireData.getElementsByTagName('DataTable')               
                    for i in DataTable:
                        RmRow = i.getElementsByTagName('Row')
                        for inx, row_tags in enumerate(RmRow):
                            assert RmRow[inx].getAttribute("BottleNumber") ==  str(inx+1)
                            assert RmRow[inx].getAttribute("index") ==  str(inx)
                            assert RmRow[inx].getAttribute("FireAt")== str(pressure_value[inx])


class Test_MetaDataWriter:
    meta_data = {
    "expedition_number":"EXP", 
    "latitude":"LAT",
    "expedition_name":"EXP_NM",
    "longitude":"LON",
    "timestamp":"TMS",
    "depth":"DP",
    "airpressure":"AP",
    "datetime":"DT", 
    "station_name": "ST"
}
    metadata_writer_obj = MetaDataWriter('test_docs\\test_setup_file.psa', meta_data)
    def test_create_new_prompt_tag(self):
        try:
            with open('test_docs\\test_setup_file.psa','r') as f:
                xmldoc = minidom.parse(f)        
                HeaderForm = xmldoc.getElementsByTagName('HeaderForm')
                RmRow = [i.getElementsByTagName('Prompt') for i in HeaderForm]
                assert len(RmRow[0]) == len(self.meta_data)
                for l in RmRow:
                    for inx, tag in enumerate(l):
                        assert tag.getAttribute("index") ==  str(inx)
        except FileNotFoundError:
            print('file is missing')

    def test_set_mata_data(self):
            with open('test_docs\\test_setup_file.psa','r') as f:
                xmldoc = minidom.parse(f)        
                HeaderForm = xmldoc.getElementsByTagName('HeaderForm')
                RmRow = [i.getElementsByTagName('Prompt') for i in HeaderForm]
                assert len(RmRow[0]) == len(self.meta_data)
                for l in RmRow:
                    for tag, key in zip(l, self.meta_data):
                        assert tag.getAttribute("value") ==   key+' = '+ str(self.meta_data[key])
