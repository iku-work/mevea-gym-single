<meta name="google-site-verification" content="5DtLJ8yjLsiba2zsWCMS2u4ofg_BdQGRbljBOS_0oSI" />
# M-Gym - a Mevea OpenAI Gym Environment 

![logo](https://github.com/iku-work/mevea-gym-single/blob/master/images/logo.JPG?raw=true)

## General info
![excavator](https://github.com/iku-work/mevea-gym-single/blob/master/images/excavator.gif?raw=true)
<br /> This is an implementation of the Mevea RL Gym with compliance to Open AI Gym.
Use your own model for training reinforcement learning algorithms.
It takes all parameters and inputs, unless they are not excluded, then creates observation and action vectors from them.
Only thing you need to do is a reward function!

    
## Requirements

- Mevea Simulation Software ver.2.4.5
- pyzmq
- numpy
    
## Setup

### On RL algorithm side:

Open cmd and run:
```
cd path_to_env
pip install -e gym-mevea-single
```

### On Mevea side:

- Add Mevea python interpreter folders to path: ../Mevea/Resourses/Python/Bin and ../Mevea/Resourses/Python/Scripts   
- Install all requirements manually using pip or mevea_setup.py.
- Make sure, that Mevea Debug Console is on.
- Create Scripts directory in the folder with mvs file and place python scripts from the mevea_files of gym folder.
- Assign mevea.py script to any input in the model.
- Change model name in config.json.
- Create reward function in reward.py.
- Use check_sim.py file to check the model. If there are any errors they will appear in LOG.txt.

## Usage

### On RL algorithm side

To use example model use following commands:
    
```
sim = gym.make('gym_mevea_single:mevea-custom-v0')
```

To use custom model provide mvs file folder as argument:
```
mvs_folder = model_folder_path
kwargs = {'mvs_folder': mvs_folder}
sim = gym.make('gym_mevea_single:mevea-custom-v0', **kwargs)
```
### Config Json
You can configure training using json file.
- Debug - if false, simulation file starts automatically, true - you need to start it manually at the generated folder
- Episode duration - simulation duration in seconds till restart
- Excluded inputs - allows to exclude input from actions
- Excluded items - allows model parts to be excluded from observation vector 
- Model name - name of the model as on mvs file, for example, Jib_Crane
- Port - port of the simulation (chosen automatically)
- Render - if true runs mevea with visualisation
- Step delay - interval of actions in seconds

## Contact details
If you have any questions, please contact:
<br />ilya.kurinov@lut.fi
