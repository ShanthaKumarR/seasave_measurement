import pytest


import os 
import sys

myDir = os.getcwd()
sys.path.append(myDir)

from src.seasave_measurement.instrument_config import SetPressure, MetaDataWriter, DataDictionary, GetPathValues
from src.seasave_measurement.Dship import Udp



@pytest.fixture(scope='module')
def get_path_values_object_init():
    return GetPathValues()

@pytest.fixture(scope='module')
def get_path_values_object():
    return GetPathValues('test_docs\\test_config_file.XMLCON', 'test_docs\\test_setup_file.psa', 'test_docs', DataDictionary, 1)

@pytest.fixture(scope='module')
def DataDictionary_obj():
    return DataDictionary

@pytest.fixture(scope='module')
def SetPressure_obj():
    return SetPressure('test_docs\\test_setup_file.psa')

@pytest.fixture(scope='module')
def Udp_obj():
    return Udp()