from gym.envs.registration import register
import pathlib

# If path is not defined, tutorial will be opened
path = pathlib.Path(__file__).parent.absolute()
mvs_path = str(path) + '\\tutorial_model\\'

register(
    id='mevea-custom-v0',
    entry_point='gym_mevea_single.envs:MeveaEnv',
    kwargs={'mvs_folder': mvs_path}
)

