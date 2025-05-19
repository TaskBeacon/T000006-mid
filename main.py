from psyflow import BlockUnit,StimBank, StimUnit,SubInfo,TaskSettings,TriggerSender
from psyflow import load_config,count_down, initialize_exp, generate_balanced_conditions

from psychopy.visual import Window
from psychopy.hardware import keyboard
from psychopy import logging, core

from functools import partial
import yaml
import sys
import serial

from src import run_trial,Controller


# 1. Load config
cfg = load_config()

# 2. Collect subject info
subform = SubInfo(cfg['subform_config'])
subject_data = subform.collect()

# 3. Load task settings
settings = TaskSettings.from_dict(cfg['task_config'])
settings.add_subinfo(subject_data)

# 4. setup triggers
settings.triggers = cfg['trigger_config']
ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write([1, 225, 1, 0, (code)]),
    post_delay=0,
    on_trigger_start=lambda: ser.open() if not ser.is_open else None,
    on_trigger_end=lambda: ser.close()
)

# 5. Set up window & input
win, kb = initialize_exp(settings)
# 6. Setup stimulus bank
stim_bank = StimBank(win,cfg['stim_config']).preload_all()
# stim_bank.preview_all() 


# 7. Setup controller across blocks
settings.controller=cfg['controller_config']
settings.save_to_json() # save all settings to json file
controller = Controller.from_dict(settings.controller)


# show instruction
StimUnit(win, 'instruction_text').add_stim(stim_bank.get('instruction_text')).wait_and_continue()
StimUnit(win, 'instruction_image1').add_stim(stim_bank.get('instruction_image1')).wait_and_continue()
StimUnit(win, 'instruction_image2').add_stim(stim_bank.get('instruction_image2')).wait_and_continue()

all_data = []
for block_i in range(settings.total_blocks):
    # 8. setup block
    count_down(win, 3, color='white')
    block = BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions(func=generate_balanced_conditions) \
    .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))\
    .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))\
    .run_trial(partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender))\
    .to_dict(all_data)
    
    
    block_trials = block.get_all_data()

    # Calculate for the block feedback
    hit_rate = sum(trial.get("target_hit", False) for trial in block_trials) / len(block_trials)
    total_score = sum(trial.get("feedback_delta", 0) for trial in block_trials)
    StimUnit(win, 'block').add_stim(stim_bank.get_and_format('block_break', 
                                                                block_num=block_i+1, 
                                                                total_blocks=settings.total_blocks,
                                                                accuracy=hit_rate,
                                                                total_score=total_score)).wait_and_continue()
       

final_score = sum(trial.get("feedback_delta", 0) for trial in all_data)
StimUnit(win, 'block').add_stim(stim_bank.get_and_format('good_bye', total_score=final_score)).wait_and_continue(terminate=True)

import pandas as pd
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)



