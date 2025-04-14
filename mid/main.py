
from psychopy.hardware import keyboard
from psychopy.visual import Window, TextStim
from mid.block import Block, generate_valid_conditions, assign_stimuli
from mid.mid_stimuli import MIDStimuli
from mid.get_feedback import get_mid_feedback
from mid.run_trial import run_mid_trial
from mid.settings import TaskSettings
from mid.subject import SubInfo
import yaml

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

import yaml
with open("mid/config/stimuli.yaml", "r") as f:
    stim_cfg = yaml.safe_load(f)

print("Loaded stim_cfg:", stim_cfg)


# 3. Stimuli
with open("mid/config/stimuli.yaml") as f:
    stim_cfg = yaml.safe_load(f)
stimuli = MIDStimuli(win, stim_cfg)

# 4. Build and run blocks
blocks = []
for i in range(settings.total_blocks):
    block = Block(
        block_id=i + 1,
        settings=settings,
        stim_map={"win": "circle", "lose": "square", "neut": "triangle"},
        window=win,
        keyboard=kb,
        generate_conditions_func=generate_valid_conditions,
        assign_stimuli_func=assign_stimuli,
        seed=settings.block_seed[i]
    )
    blocks.append(block)

# 5. Initialize adaptive tracker and points
target_dur_tracker = {
    c: {'hits': 0, 'total': 0, 'duration': settings.extras['initial_target_duration']}
    for c in settings.cue_types
}
total_points = 0

# 6. Run each block
for block in blocks:
    for cond, stim in block.trials:
        result, total_points = run_mid_trial(
            win, kb, settings, cond, stim,
            stimuli.cue_map, stimuli.target_map,
            target_dur_tracker, total_points
        )
        block.results.append(result)

    # Block feedback
    text, summary = get_mid_feedback(block.results, block.block_id)
    while not kb.getKeys(['space']):
        TextStim(win, text=text, height=0.6, color='black', wrapWidth=25).draw()
        win.flip()
