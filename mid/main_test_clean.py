import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from mid.TaskSettings import TaskSettings
from mid.SubInfo import SubInfo
import yaml
from psychopy.visual import Window
from psychopy.hardware import keyboard
from mid.StimBank import StimBank
from functools import partial
from mid.BlockUnit import BlockUnit, generate_balanced_conditions, assign_stimuli
from mid.run_mid_trial import run_mid_trial
from mid.AdaptiveController import AdaptiveController
from psychopy import logging, core


with open('mid/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# subform_config = {
#     'subinfo_fields': config.get('subinfo_fields', []),
#     'subinfo_mapping': config.get('subinfo_mapping', {})
# }

# subform = SubInfo(subform_config)
# subject_data = subform.collect()

subject_data={'subject_id': '123', 'subject_name': '123', 'experimenter': '123', 'gender': 'Male', 'race': 'Caucasian'}    
# 2. Load settings
# Flatten the config
task_config = {
    **config.get('window', {}),
    **config.get('task', {}),
    **config.get('timing', {})  # ← don't forget this!
}

settings = TaskSettings.from_dict(task_config)
settings.add_subinfo(subject_data)

logging.setDefaultClock(core.Clock())
logging.LogFile(settings.log_file, level=logging.DATA, filemode='a')
logging.console.setLevel(logging.INFO)

# 2. Set up window & input
win = Window(size=settings.size, fullscr=settings.fullscreen, screen=1,
             monitor=settings.monitor, units=settings.units, color=settings.bg_color,
             gammaErrorPolicy='ignore')
kb = keyboard.Keyboard()
aaa=1
bbb=2
settings.frame_time_seconds = win.getMsPerFrame()[0]/1000
settings.win_fps = win.getActualFrameRate()

# Assuming 
stim_bank = StimBank(win)
# Preload all for safety

stim_config={
    **config.get('stimuli', {})
}
stim_bank.add_from_dict(stim_config)
stim_bank.preload_all()


stim_map = stim_bank.get_selected([
    "cue_win", "cue_lose", "cue_neut",
    "target_win", "target_lose", "target_neut"
])
# 4. setup experiment
block = BlockUnit(
    block_id="block1",
    block_idx=0,
    settings=settings,
    stim_map=stim_map,  # assumes keys like 'cue_win', etc.
    window=win,
    keyboard=keyboard
)

assign_cue_target = partial(assign_stimuli, components=["cue", "target"])
block.generate_stim_sequence(
    generate_func=generate_balanced_conditions,
    assign_func=assign_cue_target
)
block.describe()

config_controller = {
    **config.get('controller', {})
    }
controller = AdaptiveController.from_dict(config_controller)
block.run_trial(
    partial(run_mid_trial, stim_bank=stim_bank, controller=controller)
)

