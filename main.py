from psyflow import TaskSettings
from psyflow import SubInfo
from psyflow import StimBank
from psyflow import BlockUnit
from psyflow import StimUnit
from psyflow import TriggerSender
from psyflow import TriggerBank
from psyflow import generate_balanced_conditions, count_down

from psychopy.visual import Window
from psychopy.hardware import keyboard
from psychopy import logging, core

from functools import partial
import yaml
import sys
import serial

from src import run_trial,Controller



# 1. Load config
with open('config/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 2. collect subject info
subform_config = {
    'subinfo_fields': config.get('subinfo_fields', []),
    'subinfo_mapping': config.get('subinfo_mapping', {})
}

subform = SubInfo(subform_config)
subject_data = subform.collect()
if subject_data is None:
    print("Participant cancelled — aborting experiment.")
    sys.exit(0)


# 3. Load task settings
# Flatten the config
task_config = {
    **config.get('window', {}),
    **config.get('task', {}),
    **config.get('timing', {})  # ← don't forget this!
}

settings = TaskSettings.from_dict(task_config)
settings.add_subinfo(subject_data)



# 4. Set up window & input
win = Window(size=settings.size, fullscr=settings.fullscreen, screen=1,
             monitor=settings.monitor, units=settings.units, color=settings.bg_color,
             gammaErrorPolicy='ignore')
kb = keyboard.Keyboard()
win.mouseVisible = False
logging.setDefaultClock(core.Clock())
logging.LogFile(settings.log_file, level=logging.DATA, filemode='a')
logging.console.setLevel(logging.INFO)
settings.frame_time_seconds =win.monitorFramePeriod
settings.win_fps = win.getActualFrameRate()

# 5. Setup stimulus bank
stim_bank = StimBank(win)
# Preload all for safety

stim_config={
    **config.get('stimuli', {})
}
stim_bank.add_from_dict(stim_config)
stim_bank.preload_all()


# 6. Setup trigger
trigger_config = {
    **config.get('triggers', {})
}
trigger_bank = TriggerBank(trigger_config)
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, (code)]),
    post_delay=0,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)

# 7. setup controller
controller_config = {
    **config.get('controller', {})
    }
controller = Controller.from_dict(controller_config)


# show instruction
StimUnit(win, 'instruction_text').add_stim(stim_bank.get('instruction_text')).wait_and_continue()
StimUnit(win, 'instruction_image1').add_stim(stim_bank.get('instruction_image1')).wait_and_continue()
StimUnit(win, 'instruction_image2').add_stim(stim_bank.get('instruction_image2')).wait_and_continue()
count_down(win, 3, color='white')
all_data = []
for block_i in range(settings.total_blocks):
    # 8. setup block
    block = BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=keyboard
    )

    block.generate_conditions(func=generate_balanced_conditions)

    @block.on_start
    def _block_start(b):
        print("Block start {}".format(b.block_idx))
        trigger_sender.send(trigger_bank.get("block_onset"))
    @block.on_end
    def _block_end(b):     
        print("Block end {}".format(b.block_idx))
        trigger_sender.send(trigger_bank.get("block_end"))

    
    # 9. run block
    block.run_trial(
        partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender, trigger_bank=trigger_bank)
    )
    
    block.to_dict(all_data)
    
    # Filter trials for block_0
    block_trials = [trial for trial in all_data if trial.get("block_id") == f"block_{block_i}"]

    # Calculate for the block feedback
    hit_rate = sum(trial.get("target_hit", False) for trial in block_trials) / len(block_trials)
    total_score = sum(trial.get("feedback_delta", 0) for trial in block_trials)
    StimUnit(win, 'block').add_stim(stim_bank.get_and_format('block_break', 
                                                                block_num=block_i+1, 
                                                                total_blocks=settings.total_blocks,
                                                                accuracy=hit_rate,
                                                                total_score=total_score)).wait_and_continue()
    if block_i+1 < settings.total_blocks:
       count_down(win, 3, color='white')
    if block_i+1 == settings.total_blocks:
        final_score = sum(trial.get("feedback_delta", 0) for trial in all_data)
        StimUnit(win, 'block').add_stim(stim_bank.get_and_format('good_bye', total_score=final_score)).wait_and_continue(terminate=True)
    
import pandas as pd
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)



