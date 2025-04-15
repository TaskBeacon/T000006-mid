from mid.settings import TaskSettings
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

    
# 2. Load settings
# Flatten the config
task_config = {
    **config.get('window', {}),
    **config.get('task', {}),
    **config.get('timing', {})  # ← don't forget this!
}

settings = TaskSettings.from_dict(task_config)

# 2. Set up window & input
win = Window(size=settings.size, fullscr=settings.fullscreen, screen=1,
             monitor=settings.monitor, units=settings.units, color=settings.bg_color,
             gammaErrorPolicy='ignore')
kb = keyboard.Keyboard()

# Assuming 
stim_bank = StimBank(win)
# Preload all for safety

stim_bank.add_from_dict(
    fixation={"type": "text", "text": "+"},
    cue_win={"type": "circle", "radius": 4, "fillColor": "magenta","lineColor": ""},
    cue_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "yellow","lineColor": ""},
    cue_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "cyan","lineColor": ""},
    target_win={"type": "circle", "radius": 4, "fillColor": "black","lineColor": ""},
    target_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "black","lineColor": ""},
    target_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "black","lineColor": ""}
)
stim_bank.preload_all()


stim_map = stim_bank.get_selected([
    "cue_win", "cue_lose", "cue_neut",
    "target_win", "target_lose", "target_neut"
])
# 4. setup experiment
block = BlockUnit(
    block_id="block1",
    settings=settings,
    stim_map=stim_map,  # assumes keys like 'cue_win', etc.
    window=win,
    keyboard=keyboard,
    seed=123
)

assign_cue_target = partial(assign_stimuli, components=["cue", "target"])
block.generate_stim_sequence(
    generate_func=generate_balanced_conditions,
    assign_func=assign_cue_target
)


logging.setDefaultClock(core.Clock())
logging.LogFile('test.log', level=logging.DATA, filemode='a')
logging.console.setLevel(logging.INFO)


controller = AdaptiveController(step=0.02, target_accuracy=0.66)
block.run_trial(
    partial(run_mid_trial, stim_bank=stim_bank, controller=controller)
)

