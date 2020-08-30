'''
2020, Copyright Ilya Kurinov
============================
This is a module for reading xml file of the model.
It gets
'''
import xml.etree.ElementTree as ET
import pathlib
import json
import os
from datetime import datetime


# Class containing methods to process simulation xml file with application of the config.json file
# Need fix: input from json file is case sensitive, as well as reading xml ==> normalize data to the lowercase
# Add notification that config is not found, corrupt or has wrong structure
# Add notification that model xml file is not found, corrupt or has wrong structure
# Add notification that no such tag exist

################OR####################


class MultipleScriptsError(Exception):
    def __init__(self, value):
        self.value = 'Error: {} mevea.py scripts are connected to the simulation! Leave one!'.format(value)
    def __str__(self):
        return repr(self.value)

class ScriptNotConnectedError(Exception):
    def __init__(self):
        self.value = 'Error: mevea.py script is not connected to the input! Connect to any input!'
    def __str__(self):
        return repr(self.value)

class NoScriptError(Exception):
    def __init__(self):
        self.value = 'Error: No script was attached to the Mevea simulation!'
    def __str__(self):
        return repr(self.value)

class XMLreader:

    def __init__(self):
        
        # Get useful data from the config.json file
        self.current_dir_path, self.model_name, self.exclude, self.excluded_inputs = self.read_config_json()

        log_file_dir = str(self.current_dir_path) + '\LOG.txt'
        self.log_file = open(log_file_dir, 'w+')


        # Find simulation model xml file
        self.model_file_path = '{}\{}\{}.{}'.format(str(self.current_dir_path), '..', str(self.model_name), 'xml')

        # Open file
        self.xmldoc = ET.parse(self.model_file_path)

        # List containing general tags from the model xml file
        self.list_model_keys = ['Bodies', 'Constraints', 'Dummies']
        self.list_force_keys = ['B2BM', 'B2BF', 'Motor']
        self.list_powertrain_keys = ['Gears', 'Differentials', 'Planets']        
        self.list_sensors_keys = [
            'LaserScanners',            'VisLaserScanners',     'PsysMassSensors',
            'AccelerationSensors',      'DistanceSensors',      'GyroscopicSensors',
            'AngularVelocitySensors',   'AngleSensors',         'CollisionSensors',
            'GpsSensors',               'LogLengthSensors',     'TippingSensors',
            'SoilTransferSensors',      'ContainerDetectors',   'RoadCompactionSensors',
            'LogAmountSensors',         'LogLatheSensors',      'PilingSensors', 
            'DrillingSensors',          'VirtualVelocityFields'
            ]

        # Combine them into dictionaries for use in the modelparameters.py
        self.all_dictionaries = [
                dict.fromkeys(self.list_model_keys, []),
                dict.fromkeys(self.list_force_keys, []),
                dict.fromkeys(self.list_powertrain_keys, []),
                dict.fromkeys(self.list_sensors_keys, [])
                ]

        
    
    # Method for reading config.json file
    def read_config_json(self):

        # Get path of the current file
        path = pathlib.Path(__file__).parent.absolute()
        # config.json is in the same folder ==>
        config_file =  '{}\{}'.format(str(path),'config.json' )
        
        # Open read config file
        with open(config_file) as config_file:
            data = json.load(config_file)
            name = data['model_name']

        # Clean excluded items from spaces and put to lower case
        excluded = []
        for item in data['excluded_items']:
            cleaned_item = item.replace(" ", "")
            cleaned_lower = cleaned_item.lower()
            excluded.append(cleaned_lower)

        # Clean excluded inputs from spaces and put to lowercase
        excluded_inputs = []
        for model_input in data['excluded_inputs']:
            cleaned_input = model_input.replace(" ", "")
            cleaned_input_lower = cleaned_input.lower()
            excluded_inputs.append(cleaned_input_lower)

        self.render = data['render']
        self.delay = data['step_delay[s]']
        self.port = data['port']
        self.episode_duration = data['episode_duration[s]']

        return path, name, excluded, excluded_inputs

    # Function for removing spaces and change to lowercase of the instances
    def normalize_value(self, value):
        cleaned_item = value.replace(" ", "")
        cleaned_lower = cleaned_item.lower()
        return cleaned_lower

    
    def get_dt(self):
        
        # Find model element 
        dt = self.xmldoc.find('Model').attrib['dt']

        return dt       
    

    def read_xml(self):
        
        #Get root of the xml file
        root = self.xmldoc.getroot()

        # Keys of the dictionary with general tags
        model_items = ['Main', 'Forces', 'PowerTrain', 'VirtualSensors']
         
        # Get instances of the Mevea model and save them to the dictionary 
        for item in model_items:
            element_index = model_items.index(item)
            element_dictionary = self.all_dictionaries[element_index]

            if item == 'Main':
                element =  root
            else:
                element =  root.find(item)

            for key in element_dictionary.keys():
                if self.normalize_value(key) not in self.exclude: 
                    if element:
                        element_type = element.find(key)
                        if element_type:
                            children = []
                            for child in element_type:
                                if self.normalize_value(child.tag) not in self.exclude:   
                                    children.append(child.tag)
                            element_dictionary[key] = children

        # Get script name 
        try:
            scripts = root.find('Scripting').find('Script')
        except NoScriptError as e:
            self.log_file.write('{}:{}'.format(datetime.now(),e))
            raise
        
        try:
            self.script_name = ''
            scripts_count = 0

            for child in scripts:
                
                folder, delim, script = child.get('fileName').rpartition('/')

                if script == 'mevea.py':
                    self.script_name = child.tag
                    scripts_count += 1

            if scripts_count > 1:
                raise MultipleScriptsError(scripts_count)

        except MultipleScriptsError as e:
            self.log_file.write('{}:{}'.format(datetime.now(),e))
                

        # Add inputs separately
        inputs = []
        self.script_input = ''     

        try:
            for model_input in root.find('Inputs'):
                if self.normalize_value(model_input.tag) not in self.excluded_inputs:
                    inputs.append(model_input.tag)

                if model_input.get('scriptName') == self.script_name:
                    self.script_input = model_input.tag

            if self.script_input == '':
                raise ScriptNotConnectedError()

        except ScriptNotConnectedError as e:
            self.log_file.write('{}:{}'.format(datetime.now(),e))


        # Add DataSources separately 
        ds_list = []
        data_sources = root.find('DataSources')

        if self.normalize_value('DataSources') not in self.exclude:
            for ds in data_sources:
                if self.normalize_value(ds.tag) not in self.exclude:
                    ds_list.append(ds.tag)
       

        # return model, forces, powertrain, sensors, inputs
        return self.all_dictionaries[0], self.all_dictionaries[1], self.all_dictionaries[2],self.all_dictionaries[3], ds_list, inputs

xml = XMLreader()
xml.read_xml()