import xmlreader as xml


class GObject:
    pass

class GSolver:
    pass

class GDict:
    pass

class ModelParameters():

    def __init__(self):

        self.xml_reader = xml.XMLreader()

        # Read xml file
        self.model, self.forces, self.powertrain, self.sensors, self.ds_list, self.inputs = self.xml_reader.read_xml()

        self.script_name = self.xml_reader.script_name
        self.script_input = self.xml_reader.script_input
        self.delay = self.xml_reader.delay

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


    def make_param(self, GObject, GSolver, GDict):
        # Initiate Mevea Classes
        self.Gobject = GObject
        self.Gsolver = GSolver
        self.Gdict = GDict


    def set_parameters(self):
        #model, force, powertrain, sensors = xml.XMLreader()
        pass

        return 0

    def get_parameters(self):

        self.Gobject.data['values'] = []

        # Add values of the model
        self.add_values(self.model, self.model_items)

        # Add values of the forces in the model
        self.add_values(self.forces, self.force_items)
        
        # Add values of the powertrain
        self.add_values(self.powertrain, self.powertrain_items)
        
        # Add values of the sensors in the model
        self.add_values(self.sensors, self.sensors_parameters)


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

        for ds in self.ds_list:
            obs_len += 1

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



    def add_values(self, items_dict, param_dict):    

        for item_key in items_dict.keys():
            
            for item in items_dict[item_key]:
                
                if len(item)!= 0:
                    
                    for parameter in param_dict[item_key]:
                        
                        # Put here saving to csv file
                        #print(item, parameter)
                        
                        parameter_value = self.Gsolver.getParameter(item, parameter)
                        self.Gobject.data['values'].append(parameter_value)
 
            #for parameter in self.model_items['Bodies']:
            #    parameter_value = self.Gsolver.getParameter(model_item_key, parameter)
            #    self.Gobject.data['values'].append(parameter_value)

    def get_model_inputs(self):

        self.Gobject.data['inputs'] = []

        for model_input in self.inputs: 
            
            input_obj = self.Gdict[model_input]

            self.Gobject.data['inputs'].append(input_obj)

        return 0

    def get_parameters_values(self):
        
        # Get values of the observation and save thm to list
        param_values = []
        
        for parameter in self.Gobject.data['values']:
            param_values.append(parameter.value())
        
        for ds in self.ds_list:
            param_values.append(self.Gdict[ds].getDsValue())
        return param_values

    def set_model_inputs(self,inputs_list):

        for inp in inputs_list:
            index = inputs_list.index(inp)
            self.Gobject.data['inputs'][index].setInputValue(inp)

