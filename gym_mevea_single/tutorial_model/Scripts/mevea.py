import json
import zmq
import numpy as np

import modelparameters as mp
import worker as wrk
import reward

#Executed at the loading of script
def initScript():
    
    # Get parameters and inputs lists 
    GDict['parameters'] = mp.ModelParameters()
    GDict['parameters'].make_param(GObject, GSolver, GDict)
    GDict['parameters'].get_parameters()
    GDict['parameters'].get_model_inputs()

    GDict['script'] = GDict['parameters'].script_name
    GDict['script_input'] = GDict['parameters'].script_input

    # Create socket
    GDict['worker'] = wrk.Worker(GDict['parameters'].port)

    # Get reward object
    GDict['reward'] = reward.Reward(GObject, GSolver, GDict, MVec3)

    # Get observation params
    param_values = GDict['parameters'].get_parameters_values()

    # Send request with init worker state
    request = [param_values, 0, True, 'in']
    GDict['worker'].send(request)

    # Get reply that reset successful
    reply = GDict['worker'].recv() 

    #print("Finished", reply)

    GDict['done'] = False
    GDict['episodeTime'] = GDict['parameters'].episode_duration
    GDict['routerState'] = 'st'
    GDict['delay'] = GDict['parameters'].delay
    GDict['oldTime'] = 0
    GDict['reward'].custom_start()

    GDict['reseted'] = 0

#Executed every 10 ms
def callScript(deltaTime, simulationTime ):
    
    if simulationTime - GDict['oldTime'] >= GDict['delay']:

        GDict['reward'].custom_tick()

        # Get observation params
        param_values = GDict['parameters'].get_parameters_values()
        reward = GDict['reward'].get_reward()
        info = 'ti' 

        # Get reply from the agent and unpack them
        reply = GDict['worker'].communicate([param_values, reward, GDict['done'], info])
        actions = reply[0]
        GDict['routerState'] = reply[1]

        # Assign actions to inputs 
        GDict['parameters'].set_model_inputs(actions)

        GDict['oldTime'] = simulationTime


    # Check if the episode is over 
    if simulationTime >= GDict['episodeTime']: # or GDict['routerState'] == 'rs':
        GDict['done'] = True
    else:
        GDict['done'] = False

    # If episode ended or call for reset received, restart simulation
    if GDict['done'] and GDict['reseted'] == 0:
        GSolver.restartSimulation()
        GDict['reseted'] += 1

    return 0