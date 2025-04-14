from mid.settings import TaskSettings
from mid.subject import SubInfo
import yaml
from psychopy.visual import Window
from psychopy.hardware import keyboard

# 1. collect subject info
with open('mid/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

subform_config = {
    'subinfo_fields': config.get('subinfo_fields', []),
    'subinfo_lang': config.get('subinfo_lang', {})
}

subform = SubInfo(subform_config, language='cn')
subject_data = subform.collect()


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

# 3. setup stimuli
from psychopy.visual import Circle, Rect, Polygon
from mid.StimBank import StimBank

# Assuming 
stim_bank = StimBank(win)
# --- Cue Stimuli ---
@stim_bank.define("cue_win")
def _cue_circle(win):
    return Circle(win, radius=4, fillColor="magenta", lineColor=None)

@stim_bank.define("cue_lose")
def _cue_square(win):
    return Rect(win, width=8, height=8, fillColor="yellow", lineColor=None)

@stim_bank.define("cue_neut")
def _cue_triangle(win):
    return Polygon(win, edges=3, size=8, fillColor="cyan", lineColor=None)

# --- Target Stimuli (Black) ---
@stim_bank.define("target_win")
def _target_circle(win):
    return Circle(win, radius=4, fillColor="black", lineColor=None)

@stim_bank.define("target_lose")
def _target_square(win):
    return Rect(win, width=8, height=8, fillColor="black", lineColor=None)

@stim_bank.define("target_neut")
def _target_triangle(win):
    return Polygon(win, edges=3, size=8, fillColor="black", lineColor=None)

# Preload all for safety

stim_bank.add_from_dict(
    cue_win={"type": "circle", "radius": 4, "fillColor": "magenta","lineColor": ""},
    cue_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "yellow","lineColor": ""},
    cue_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "cyan","lineColor": ""},
    target_win={"type": "circle", "radius": 4, "fillColor": "black","lineColor": ""},
    target_lose={"type": "rect", "width": 8, "height": 8, "fillColor": "black","lineColor": ""},
    target_neut={"type": "polygon", "edges": 3, "size": 8, "fillColor": "black","lineColor": ""}
)

stim_bank.describe("cue_neut")
stim_bank.preload_all()
stim_bank.preview_all()
stim_bank.preview_selected(['cue_neut'])
stim_bank.rebuild('cue_neut', fillColor='red')
stim_bank.preview_selected(['cue_neut'])

from mid.BlockUnit import BlockUnit, generate_balanced_conditions, assign_stimuli
# 4. setup experiment
block = BlockUnit(
    block_id="block1",
    settings=settings,
    stim_map=stim_bank.get_group("cue"),  # assumes keys like 'cue_win', etc.
    window=win,
    keyboard=keyboard,
    seed=123
)

# Chain setup: generate conditions and assign stimuli
block.generate_stim_sequence(
    generate_func=generate_balanced_conditions,
    assign_func=assign_stimuli
)
block.conditions
block.stimuli
block.describe()
block.stim_map





