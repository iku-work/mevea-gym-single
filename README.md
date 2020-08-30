# Mevea-Gym-Toolbox

## General info
This is an implementation of the Mevea RL Gym with compliance to Open AI Gym.

    
## Requirements

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

- Add Mevea python interpreter to path. Then install all requirements manually using pip or mevea_setup.py.
- Create Scripts directory in the folder with mvs file and place python scripts from the mevea_files gym folder.
- Assign mevea.py script to any input in the model.
- Change model name in config.json
- Use check_sim.py file to check the model. If there are any errors they will appear in LOG.txt

## Usage

### On RL algorithm side

To use example model use following commands:
    
```
sim = gym.make('gym_mevea_single:mevea-custom-v0')
```

To use custom model provide mvs file folder as argument:
```
