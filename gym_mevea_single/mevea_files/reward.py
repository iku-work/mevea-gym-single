'''
==========================================================================
This is a file where you can write your own implementation of the reward
function or any other custom function:

get_reward:     calculate your custom reward here.      returns reward.
custom_start:   called at the start of the simulation   returns your value
custom_tick:    called at each timestep                 returns your value
==========================================================================
'''

from random import uniform
import math

class Reward:

    def __init__(self, GObject, GSolver, GDict, MVec3):
        
        # Get Mevea classes
        self.GObject = GObject
        self.GSolver = GSolver
        self.GDict   = GDict
        self.MVec3   = MVec3

    def get_reward(self):

        distance = 0

        for coordinate in self.GDict['coordinates']:

            body_1_value = self.GSolver.getParameter('Body1',coordinate).value()
            index = self.GDict['coordinates'].index(coordinate)
            body_2_value = self.GDict['Dummy_Pos_list'][index]
            pos_difference = (body_2_value - body_1_value) ** 2
            distance += pos_difference
        
        distance = math.sqrt(distance)

        return math.exp(-distance)

    def custom_start(self):
        
        self.GDict['coordinates'] = ['x', 'y', 'z']
        self.GDict['Dummy_Pos_list'] = []

        for coordinate in self.GDict['coordinates']:
            self.GDict['Dummy_Pos_list'].append(self.GSolver.getParameter('Body1',coordinate).value())

        self.GDict['Dummy_Pos'] = self.MVec3(self.GDict['Dummy_Pos_list'][0] + uniform(-1, -0.5), self.GDict['Dummy_Pos_list'][1] + uniform(-1, 1), self.GDict['Dummy_Pos_list'][2] + uniform(-1, 1))
        self.GDict['Dummy1'].setPosition(self.GDict['Dummy_Pos'])



    # Will be called each timestep
    def custom_tick(self):

        self.GDict['Dummy1'].setPosition(self.GDict['Dummy_Pos'])
