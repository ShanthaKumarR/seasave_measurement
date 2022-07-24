import os 
from xml.dom import minidom 
import pytest
from instrument_config import IOWWaterSampler
#from instrument_config import DataDictionary

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
    