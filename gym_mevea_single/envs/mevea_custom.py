import gym
from gym import spaces
import numpy as np
import json
import xml.etree.ElementTree as ET
import pathlib
from pathlib import Path
import os
import subprocess
from multiprocessing import Process
import shutil
import errno
import time
import zmq
import uuid
import msvcrt
import sys

#from stable_baselines.common.env_checker import check_env

class MeveaEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}

  def __init__(self, mvs_folder):
    super(MeveaEnv, self).__init__()

    self.dirs_exist = self.check_dir(mvs_folder)

    if self.dirs_exist:
        self.router = Router()
        self.port = self.router.start()
        
        # Call method for obtaining model parameters from simulation xml file
        self.parameters = ModelParameters(mvs_folder, self.port)
        self.model_file_path = self.parameters.model_file_path
        # Get amount of the parameters in the observation vector
        self.obs_len = self.parameters.get_obs_len()
        
        # Get amount of the parameters in the action vector
        self.act_low_list, self.act_high_list, self.act_len = self.parameters.get_act_len()

        # Create observation and action numpy array
        self.observation = np.zeros(self.obs_len, dtype=np.float32)
        self.action = np.zeros(self.act_len, dtype=np.float32)
        self.action_low = np.array(self.act_low_list, dtype=np.float32)
        self.action_high = np.array(self.act_high_list, dtype=np.float32)

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self.observation.shape)
        self.action_space = spaces.Box(low=self.action_low, high=self.action_high, shape=self.action.shape)

        # Variable stating if simulation was terminated
        self.closed =  True
        
        # Create Mevea workers
        self.mev_worker = MevMultiProc(self.model_file_path, self.port)

        # Create simulation parameters
        self.info = {'workerState':'ti'}
        self.done = [True]
        self.reward = 0
        self.observation = []

        self.greeting()

    else:
        sys.exit()

  # Returns Box observation space 
  def get_observation_space(self):
    return spaces.Box(low=-np.inf, high=np.inf, shape=self.observation.shape)

  # Returns Box action space
  def get_action_space(self):
    return spaces.Box(low=self.action_low, high=self.action_high, shape=self.action.shape)

  def dt(self):
    return self.parameters.dt

  def step(self, action):

    request = self.router.recv()

    # Unpack values
    self.observation = np.array(request[0])
    self.reward = request[1]
    self.done = request[2]
    self.info['workerState'] = request[3]

    '''
    =====================================
    Send response structure 
    =====================================
    [[action], 'current state']
    [[......],        'step']
    '''

    self.router.send([action.tolist(), 'st'])

    if msvcrt.kbhit():
        self.close()


    return self.observation, self.reward, self.done, self.info
  
  def reset(self):
    
    # Flush rest of the simulation variables
    while self.info['workerState'] != 'in':
      
      '''
      Receive observation:
      [[observation], reward, done,   'info']
      [[...........],    0,   False,  'in'] 
      '''
      request = self.router.recv()

      # Unpack values 
      self.observation = np.array(request[0])
      self.done = request[2]
      self.info['workerState'] = request[3]

      '''
      Send reset call till reseted
            # [[action],  'current state']
      # [[......],  'reset']
      '''

      if self.info['workerState'] == 'in':
        reply = [[], 'done']
        
      else:
        
        reply = [[], 'rs']
      self.router.send(reply)

    return self.observation  # reward, done, info can't be included
  
  def set_state(self):
    pass

  def get_state(self):
    pass

  def render(self, mode='', close=False):

    pass
  
  def close(self):

      print('Closing simulation environment!')
      self.router.close()
      self.mev_worker.terminate()
      self.parameters.delete()
      sys.exit()
      
  def check_dir(self, mvs_folder):

      if not Path.exists(Path(mvs_folder)):
          print('Error: Directory {} not found'.format(mvs_folder))
          return False
      elif not Path.exists(Path(mvs_folder + '\Scripts\config.json')):
          print('Error: Config file {} not found'.format(mvs_folder + '\Scripts\config.json'))
          return False
      else:
          return True

  def greeting(self):
        print('\n.................:!*%%*!::..............................................................................................')
        print('............::!*%$$$$%%%%**!!::.........................................................................................')
        print('.......::!*%$$$$$$%%!!!**%%%%%**!::.....................................................................................')
        print('...:!*%%$$$$$$%*!:..::...:!!**%%%%%**!::...:::...........::.................::!!!::.....................................')
        print('...!$$$$$%*!::..:!*%$%**!::..::!!*%%%$$:...@BS&!......:%SBS!............:%&###&&&###&!..................................')
        print('...!$$%%%*!!!!%%$$$$$%%%%%**!!:!*%$$$$$:...@BS#B&*..:$SS#BB!..........:@BB@!:.....:!*:.:.........:......::....:::.......')
        print('...::!*%%$$$$$$$$$%!:::!*%%%$$$$$$$$%*!....@B#.*&B#@BS$:*BB!..........@BS:.............*##*...:&S%.%S&$@&&#@%@@&##@:....')
        print('...:*%%$$$$$$$$%%%*!!:!*%$$$$$$$$%%%**!:...@B#...!&#%:..%BB!.:*****!..#B#......:&&&##%..*SB$.!SB$..$BS!:.:&BS!:.:&B@....')
        print('...!$$$$$%!:::!**%%%%%$$$$%%!:::!*%%$$$!...@B#..........%BB!.:&&&&&@:.!SB&!.....:::SB@...:&B#BS*...$B#....$B#....$B&....')
        print('...!$%%%%**!!:...::!*%%*!:..::!*%$$$$$$:...@BS..........%BB!...........:%#S#&@$$$@&BB$....:#B#:....$B#....$B#....@B&....')
        print('....::!**%%%%%**!::.....:!*%$$$$$$%%*!:....!**..........:**:..............:!*%%$%%*!:....:#B@:.....!**....!**....!*!....')
        print('........::!!**%%%%%**!%%$$$$$$%*!::.....................................................*BB%............................')
        print('.............::!***%%$$$$%*!::.........................................................:%$!.............................')
        print('..................:!!**!:...............................................................................................')
        print('========================================================================================================================')
        print('                                Welcome to M-Gym!  To abort training press any key... ')
        print('========================================================================================================================')

class ModelParameters():

  def __init__(self, mvs_path, port):

    self.path = mvs_path
    
    self.copied = 'tutorial_model' not in self.path

    if self.copied:
      self.current_id = uuid.uuid1()
      self.new_folder = '{}\{}\{}'.format(mvs_path,'..',self.current_id) 
      self.copy(mvs_path,self.new_folder)
      self.path = self.new_folder

    else:
        self.new_folder = mvs_path


    self.xml_reader = XMLreader(self.new_folder,port)
    self.model_file_path = self.xml_reader.mvs_path

    # Read xml file
    self.model, self.forces, self.powertrain, self.sensors, self.inputs = self.xml_reader.read_xml()

    #Bodies related parameters (positions XYZ, Euler parameters, )
    bodies_parameters = [
        'x',    'y',        'z',        'ep0',      'ep1', 'ep2',
        'ep3',  'xd',       'yd',       'zd',       'wx',   'wy',
        'wz',   'CollFx',   'CollFy',   'CollFz'
        ]


    constraints_parameters = [
        'Fxl', 'Fyl', 'Fzl', 'Txl', 'Tyl',
        'Tzl', 'FxJ', 'FyJ', 'FzJ', 'TxJ',
        'TyJ', 'TzJ'
        ]
    
    dummies = [
        'x',    'y',    'z',    'ep0',      'ep1',
        'ep2', 'ep3',   'xd',   'yd',       'zd',
        'wx',   'wy',   'wz',   'CollFx',   'CollFy',
        'CollFz'
        ]
    
    data_sources_parameters = ['Value'] 
    

    self.model_items = {
        'Bodies'        : bodies_parameters, 
        'Constraints'   : constraints_parameters,
        'Dummies'       : dummies,
        'DataSources'   : data_sources_parameters, 
        }

    #Forces related parameters
    B2BM_parameters = ['T', 'Ti', 'r', 'dr', 'rd', 'TxJl', 'TyJl', 'TzJl']
    B2BF_parameters = ['F', 'Fi', 'L', 'Ld', 'FxJ', 'FyJ', 'FzJ', 'FxJl', 'FyJl', 'FzJl']
    motor_parameters = ['T', 'Tl', 'Th', 'Tpt', 'Tb', 'w', 'wref', 'P', 'W', 'SFC', 'SFC_l/h', 'FC', 'FC_l', 'isRunning']

    self.force_items = {
        'B2BM'  : B2BM_parameters,
        'B2BF'  : B2BF_parameters,
        'Motor' : motor_parameters
    }

    #Powertrain related parameters
    gear_parameters = ['Gear', 'Tout', 'Tin', 'wout', 'win']
    differential_parameters = ['Tout1', 'Tout2', 'Tin', 'wout1', 'wout2', 'win', 'isLocked']
    planet_parameters = ['Tout', 'Tin', 'wout', 'win']
    
    self.powertrain_items ={
        'Gears' : gear_parameters,
        'Differentials' : differential_parameters,
        'Planets' : planet_parameters
    }


    #Sensors related parameters
    vislaserscanners_parameters = ['minimumDistance']
    laserscanner_parameters = ['D', 'minimumDistance']
    psysmasssensor_parameters = ['Mass', 'Derivative', 'Volume']
    accelerationsensor_parameters = ['xdd', 'ydd', 'zdd', 'mdd']
    distancesensor_parameters = ['Dx', 'Dy', 'Dz', 'Dm']
    gyroscopicsensor_parameters = ['wx', 'wy', 'wz', 'wm']
    angularvelocitysensor_parameters = ['wx', 'wy', 'wz', 'wm']
    anglesensor_parameters = ['rx', 'ry', 'rz', 'rm']
    collisionsensor_parameters = ['rx', 'ry', 'rz', 'rm']
    collisionsensor_parameters = ['isColliding', 'Vrel', 'nminor', 'nserious', 'ncritical', 'circumference']
    gpssensor_parameters = ['gx','gy', 'gz', 'velocity', 'heading']
    loglengthsensor_parameters = ['L', 'L_continuous']
    tippingsensor_parameters = ['cm_pos_vrt_initial_cm_x', 'cm_pos_vrt_initial_cm_y', 'cm_pos_vrt_initial_cm_z', 'cm_x', 'cm_y', 'cm_z', 'minDistance']
    soiltransfersensor_parameters = ['MassTot', 'MassLast', 'SoilTot', 'SoilLast']
    containerdetector_parameters = ['nObjects', 'gx', 'gy', 'gz', 'ep0', 'ep1', 'ep2', 'ep3']
    roadcompactionsensor_parameters = ['A_tot', 'A_target', 'A_over', 'stiffnessAvg']
    logamountsensor_parameters = ['nLogs', 'nPulp', 'nTot']
    loglathesensor_parameters = ['r', 'theta', 'psysw', 'id', 'state']
    pillingsensor_parameters = ['Depth']
    drillingsensor_parameters = ['Depth', 'SoilAmount', 'HoleDepth', 'endBearingResistanceCalculated', 'vdiff', 'tipForce', 'tipTorque', 'skinTorque', 'tipTorqueResistance', 'drillingViscosity']
    virtualvelocityfieldssensor_parameters = ['Velocity']

    self.sensors_parameters = {
        'LaserScanners' : laserscanner_parameters, 'VisLaserScanners' : vislaserscanners_parameters, 'PsysMassSensors' : psysmasssensor_parameters,
        'AccelerationSensors' : accelerationsensor_parameters, 'DistanceSensors' : distancesensor_parameters, 'GyroscopicSensors' : gyroscopicsensor_parameters,
        'AngularVelocitySensors' : angularvelocitysensor_parameters, 'AngleSensors' : anglesensor_parameters, 'CollisionSensors' : collisionsensor_parameters,
        'GpsSensors' : gpssensor_parameters, 'LogLengthSensors' : loglengthsensor_parameters, 'TippingSensors' : tippingsensor_parameters,
        'SoilTransferSensors' : soiltransfersensor_parameters, 'ContainerDetectors' : containerdetector_parameters, 'RoadCompactionSensors' : roadcompactionsensor_parameters,
        'LogAmountSensors' : logamountsensor_parameters, 'LogLatheSensors' : loglathesensor_parameters, 'PilingSensors' : pillingsensor_parameters,
        'DrillingSensors' : drillingsensor_parameters, 'VirtualVelocityFields' : virtualvelocityfieldssensor_parameters,
    }

    self.dt = self.xml_reader.get_dt()
    self.episode_duration = self.xml_reader.episode_duration
    self.port = self.xml_reader.port

  def copy(self, src, dest):
      try:
          shutil.copytree(src, dest)
      except OSError as e:
          # If the error was caused because the source wasn't a directory
          if e.errno == errno.ENOTDIR:
              shutil.copy(src, dest)
          else:
              print('Directory not copied. Error: %s' % e)
  
  def delete(self):
    if self.copied:
        try:
            shutil.rmtree(self.new_folder)
        except OSError as e:
            print("Error: %s : %s" % (self.new_folder, e.strerror))


  def calc_len(self, items_dict, param_dict):
      
    count = 0

    for item_key in items_dict.keys():
        
        for item in items_dict[item_key]:
            
            if len(item)!= 0:
                
                for parameter in param_dict[item_key]:
                    count += 1
    
    return count

  def get_obs_len(self):
      
    obs_len = 0
    items       = [self.model,          self.forces,        self.powertrain,        self.sensors]
    parameters  = [self.model_items,    self.force_items,   self.powertrain_items,  self.sensors_parameters]

    for item in items:
        index = items.index(item)
        obs_len += self.calc_len(item, parameters[index])

    return obs_len


  def get_act_len(self):
      
    count = 0
    inp_min = []
    inp_max = []

    for model_input in self.inputs: 
        inp_min.append(-1)
        inp_max.append(1)
        count += 1

    return inp_min, inp_max, count



class XMLreader:

    def __init__(self, mvs_path, port):
        
        self.mvs_path = mvs_path
        self.port = port
        self.config_path = '{}\{}'.format(mvs_path,'Scripts')
        
        # Get useful data from the config.json file
        self.current_dir_path, self.model_name, self.exclude, self.excluded_inputs = self.read_config_json()

        # Find simulation model xml file
        self.model_file_path = '{}\{}\{}.{}'.format(str(self.current_dir_path), '..', str(self.model_name), 'xml')

        # Open file
        self.xmldoc = ET.parse(self.model_file_path)
        
        # List containing general tags from the model xml file
        self.list_model_keys = ['Bodies', 'Constraints', 'Dummies', 'DataSources']
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
        

        # config.json is in the same folder ==>
        config_file =  '{}\{}'.format(str(self.config_path),'config.json' )
        

        try:
            # Open read config file
            with open(config_file, 'r') as config_file_json:
                data = json.load(config_file_json)
                name = data['model_name']
        except OSError as e:
            raise
            print('Error: {}. Make sure that config is in Scripts folder!'.format(e))
            

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

        self.debug = data['debug']
        self.render = data['render']
        self.episode_duration = data['episode_duration[s]']

        # Open read config file
        with open(config_file, 'w') as out_file:
            data.update({'port':self.port})
            json.dump(data, out_file, indent=4, sort_keys=True)
            
        return self.config_path, name, excluded, excluded_inputs

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


        # Add inputs separately
        inputs = []     
        for model_input in root.find('Inputs'):
            if self.normalize_value(model_input.tag) not in self.excluded_inputs:
                inputs.append(model_input.tag)


        # return model, forces, powertrain, sensors, inputs
        return self.all_dictionaries[0], self.all_dictionaries[1], self.all_dictionaries[2],self.all_dictionaries[3], inputs



class MevMultiProc:

    def __init__(self, mvs_path, port):
        
        self.mvs_path = mvs_path
        self.reader = XMLreader(self.mvs_path, port)
        self.model_name = self.reader.model_name
        self.render = bool(self.reader.render)
        self.sim_path = self.reader.current_dir_path
        self.debug = self.reader.debug

        if self.debug == False:
            self.start_process()
            

    def terminate(self):

        # Close all of the MeveaSolver.exe processes
        
        self.process.kill()

        # Sleep for some time
        time.sleep(2)
    
    #def msolver(self, model_name, render):
        


    def start_process(self):
        
        # Create path of the file
        path_to_file = str(self.sim_path) + '\..\{}.mvs'.format(self.model_name)

        if self.render == True:
            # Create cmd command
            command = 'MeveaSolver.exe /mvs  {}'.format(path_to_file)
        else:
            command = 'MeveaSolver.exe /headless /mvs  {}'.format(path_to_file)

        #self.process = subprocess.Popen(command, shell=False)

        self.process = subprocess.Popen(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        #os.system(command)

class Router:

                
    def start(self):

        # Create zmq context and socket
        self.context = zmq.Context.instance()
        self.client = self.context.socket(zmq.REP)
        
        self.port_selected = self.client.bind_to_random_port('tcp://*', min_port=6001, max_port=6004, max_tries=100)

        print('Worker created on port {}!'.format(self.port_selected))

        return self.port_selected

    def recv(self):

        b_request = self.client.recv()
        request = json.loads(b_request)

        return request

    def send(self, msg):

        b_reply = json.dumps(msg).encode()
        self.client.send(b_reply)


    def close(self):

        self.context.destroy()