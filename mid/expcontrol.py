from psychopy import visual, event, core, logging
import numpy as np
import pandas as pd
from psyflow.screenflow import show_static_countdown

def exp_run(win, kb, settings, trialseq, subdata):
    """
    Runs the MID task. Each trial proceeds as follows:
      1. Fixation cross.
      2. Cue stimulus (colored shape) for settings.cueDuration.
      3. Anticipation period (a blank screen) for settings.antiDuration.
      4. Target stimulus (black shape) for a dynamic duration.
         Participants respond (using settings.responseKey) during the target.
      5. Feedback is shown (hit/miss and points earned).
      6. Inter-trial interval (ITI).
      
    Point outcomes:
       - Win condition: Hit = +10; Miss = 0.
       - Lose condition: Hit = 0; Miss = –10.
       - Neutral condition: Always 0.
       
    The target duration is adjusted based on the accumulated hit rate per condition,
    aiming for an overall hit rate of ~66%.
    """
    # Setup logging
    log_filename = settings.outfile.replace('.csv', '.log')
    logging.LogFile(log_filename, level=logging.DATA, filemode='a')
    logging.console.setLevel(logging.INFO)
    event.globalKeys.clear()
    event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
    event.Mouse(visible=False)  # hide the mouse cursor

    # Prepare basic visual components
    fix = visual.TextStim(win, height=1, text="+", wrapWidth=10, color='black', pos=[0, 0])
    feedback_text = visual.TextStim(win, height=0.6, wrapWidth=25, color='black', pos=[0, 0])
    BlockFeedback = visual.TextStim(win, height=0.6, wrapWidth=25, color='black', pos=[0, 0])

    # Timing parameters
    # Use a staircase step if defined; otherwise default to 0.05 sec.
    try:
        step = settings.staircase
    except AttributeError:
        step = 0.05
    min_td = 0.1   # minimum target duration (seconds)
    max_td = 1.5   # maximum target duration (seconds)
    
    # Define stimulus mappings: cues (colored shapes) and targets (black shapes)
    cue_map = {
        'win': settings.CircleCue,    # reward cue (magenta circle)
        'lose': settings.SquareCue,   # punishment cue (yellow square)
        'neut': settings.TriangleCue    # neutral cue (cyan triangle)
    }
    target_map = {
        'win': settings.CircleProb,    # target for win condition
        'lose': settings.SquareProb,   # target for lose condition
        'neut': settings.TriangleProb  # target for neutral condition
    }
    
    # Initialize the current target duration for each condition
    target_dur = {"win": settings.ProbDuration,
                  "lose": settings.ProbDuration,
                  "neut": settings.ProbDuration}
    # Initialize hit record (cumulative) for each condition
    hit_record = {
        "win": {"hits": 0, "total": 0},
        "lose": {"hits": 0, "total": 0},
        "neut": {"hits": 0, "total": 0}
    }
    
    # Initialize overall points counter.
    total_points = 0

    # Prepare a container for block-level data using a simple namespace
    class blockdata:
        pass
    # Initialize empty data fields (using numpy arrays to allow hstacking)
    blockdata.cond = np.array([], dtype=object)           # Condition: 'win', 'lose', 'neut'
    blockdata.cue = np.array([], dtype=object)            # Cue shape label (e.g., 'circle', etc.)
    blockdata.response = np.array([], dtype=object)         # Response (settings.responseKey if hit; 0 otherwise)
    blockdata.RT = np.array([], dtype=object)             # Reaction time in ms
    blockdata.points_trial = np.array([], dtype=object)     # Points earned on the trial
    blockdata.target_dur = np.array([], dtype=object)       # Target duration (s) for the trial
    blockdata.blockNum = np.array([], dtype=object)         # Block number
    blockdata.DATA = []  # this will eventually contain the block data matrix

    # Loop through all trials in the generated trial sequence.
    for i in range(len(trialseq.conditions)):
        kb.clock.reset()
        kb.clearEvents()
        # trial_onset = core.getTime()
        
        # Get condition for the current trial: 'win', 'lose', or 'neut'
        cond = trialseq.conditions[i]
        # Select corresponding cue and target stimuli.
        cue_stim = cue_map[cond]
        target_stim = target_map[cond]
        
        # -------------------------
        # 1. Fixation
        fix.draw()
        win.flip()
        core.wait(settings.fixDuration)
        
        # -------------------------
        # 2. Cue Presentation
        cue_stim.draw()
        win.flip()
        core.wait(settings.cueDuration)
        
        # -------------------------
        # 3. Anticipation (Blank Screen)
        win.flip()  # blank screen
        core.wait(settings.antiDuration)
        
        # -------------------------
        # 4. Target Presentation and Response Collection
        target_stim.draw()
        win.flip()
        target_onset = core.getTime()
        # Use updated target duration for this condition
        resp = event.waitKeys(maxWait=target_dur[cond], keyList=settings.keyList)
        if resp:
            hit = True
            RT = core.getTime() - target_onset
        else:
            hit = False
            RT = 0

        # -------------------------
        # 5. Feedback and Point Assignment
        if cond == 'win':
            points_trial = 10 if hit else 0
        elif cond == 'lose':
            points_trial = 0 if hit else -10
        else:  # neutral condition
            points_trial = 0
        
        total_points += points_trial
        
        if hit:
            if cond == 'win':
                fb_msg = "Hit! +10 points"
            elif cond == 'lose':
                fb_msg = "Hit!"
            else:
                fb_msg = "Hit!"
        else:
            if cond == 'lose':
                fb_msg = "Miss! -10 points"
            else:
                fb_msg = "Miss!"
        fb_msg += f"\nTotal: {total_points} points"
        feedback_text.text = fb_msg
        feedback_text.draw()
        win.flip()
        core.wait(settings.fbDuration)
        
        # -------------------------
        # 6. Inter-Trial Interval (ITI)
        fix.draw()
        win.flip()
        core.wait(settings.iti)
        
        # -------------------------
        # Update Dynamic Target Duration Based on Accumulated Hit Rate
        hit_record[cond]["total"] += 1
        if hit:
            hit_record[cond]["hits"] += 1
        current_hit_rate = hit_record[cond]["hits"] / hit_record[cond]["total"]
        # Adjust target duration if hit rate deviates from 66%
        if current_hit_rate > 0.66:
            target_dur[cond] = max(target_dur[cond] - step, min_td)
        elif current_hit_rate < 0.66:
            target_dur[cond] = min(target_dur[cond] + step, max_td)
        
        # -------------------------
        # Logging Trial Data
        logging.data(f"Trial {i+1}: Block={trialseq.blocknum[i]}, Condition={cond}, Cue={trialseq.stims[i]}, "
                     f"Hit={'Yes' if hit else 'No'}, RT={int(RT*1000)}ms, Points={points_trial}, "
                     f"TotalPoints={total_points}, TargetDur={target_dur[cond]:.2f}s, HitRate={current_hit_rate:.2f}")
        
        # Append trial data to block-level containers.
        blockdata.blockNum = np.hstack((blockdata.blockNum, trialseq.blocknum[i]))
        blockdata.cond = np.hstack((blockdata.cond, cond))
        blockdata.cue = np.hstack((blockdata.cue, trialseq.stims[i]))  # e.g., 'circle', 'square', or 'triangle'
        blockdata.response = np.hstack((blockdata.response, settings.responseKey if resp else 0))
        blockdata.RT = np.hstack((blockdata.RT, int(RT * 1000)))  # in ms.
        blockdata.points_trial = np.hstack((blockdata.points_trial, points_trial))
        blockdata.target_dur = np.hstack((blockdata.target_dur, target_dur[cond]))
        
        # -------------------------
        # End-of-Block Processing
        if trialseq.BlockEndIdx[i] == 1:
            # Use current block's data only (using range based on blockdata length).
            block_indices = range(len(blockdata.RT))
            hit_RTs = [blockdata.RT[j] for j in block_indices if blockdata.response[j] != 0]
            mean_RT = np.mean(hit_RTs) if hit_RTs else 0
            block_accuracy = np.mean([1 if blockdata.response[j] != 0 else 0 for j in block_indices]) * 100
            block_points = np.sum([blockdata.points_trial[j] for j in block_indices])
            
            BlockFeedback.text = f"End of Block #{trialseq.blocknum[i]}\n"
            BlockFeedback.text += f"Mean RT: {mean_RT:.0f} ms\n"
            BlockFeedback.text += f"Accuracy: {block_accuracy:.1f}%\n"
            BlockFeedback.text += f"Block Points: {block_points}\n"
            BlockFeedback.text += "Press SPACE to continue..."
            
            # Organize block data into a dictionary and then a DataFrame.
            blockdata_np = {
                "Block": np.array(blockdata.blockNum, dtype=object).reshape(-1, 1),
                "Condition": np.array(blockdata.cond, dtype=object).reshape(-1, 1),
                "Cue": np.array(blockdata.cue, dtype=object).reshape(-1, 1),
                "Response": np.array(blockdata.response, dtype=object).reshape(-1, 1),
                "RT": np.array(blockdata.RT, dtype=object).reshape(-1, 1),
                "TrialPoints": np.array(blockdata.points_trial, dtype=object).reshape(-1, 1),
                "TargetDur": np.array(blockdata.target_dur, dtype=object).reshape(-1, 1)
            }
            temp = np.hstack(list(blockdata_np.values()))
            if trialseq.blocknum[i] == 1:
                blockdata.DATA = temp
            else:
                blockdata.DATA = np.vstack([blockdata.DATA, temp])
            
            df = pd.DataFrame(blockdata.DATA, columns=["Block", "Condition", "Cue", "Response", "RT", "TrialPoints", "TargetDur"])
            df.to_csv(settings.outfile, index=False)
            with open(settings.outfile, 'a') as f:
                f.write('\n' + ','.join(subdata))
            
            # Display block feedback until SPACE is pressed.
            while not event.getKeys(keyList=['space']):
                BlockFeedback.draw()
                win.flip()
            
            # Optional: Additional performance feedback for the next block
            if trialseq.blocknum[i] < settings.TotalBlocks:
                PerformanceFeedback = visual.TextStim(win, height=0.6, wrapWidth=25, color='black', pos=[0, 0])
                if block_points < 0:
                    PerformanceFeedback.text = (
                        "Your performance in this block was below expectation.\n"
                        "Try to respond faster in the next block.\nThanks."
                    )
                else:
                    PerformanceFeedback.text = "Good job!\nKeep it up!"
                PerformanceFeedback.text += " Press SPACE to continue..."
                while not event.getKeys(keyList=['space']):
                    PerformanceFeedback.draw()
                    win.flip()
                # Reset block data for the next block.
                blockdata.blockNum = np.array([], dtype=object)
                blockdata.cond = np.array([], dtype=object)
                blockdata.cue = np.array([], dtype=object)
                blockdata.response = np.array([], dtype=object)
                blockdata.RT = np.array([], dtype=object)
                blockdata.points_trial = np.array([], dtype=object)
                blockdata.target_dur = np.array([], dtype=object)
                # Countdown before the next block.
                show_static_countdown(win)
