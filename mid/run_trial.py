# run_mid_trial.py
from psychopy import core, event
from psychopy.visual import TextStim

def run_mid_trial(win, kb, settings, cond, stim_label,
                  cue_map, target_map, target_dur_tracker, total_points):
    # --- Fixation ---
    TextStim(win, text='+', height=1.0, color='black').draw()
    win.flip()
    core.wait(settings.extras.get('fixation_duration', 0.5))

    # --- Cue ---
    cue_map[cond].draw()
    win.flip()
    core.wait(settings.extras.get('cue_duration', 0.5))

    # --- Anticipation ---
    win.flip()
    core.wait(settings.extras.get('anticipation_duration', 0.5))

    # --- Target + response ---
    dur = target_dur_tracker[cond]
    target_map[cond].draw()
    win.flip()

    kb.clock.reset()
    kb.clearEvents()
    onset = core.getTime()
    resp = event.waitKeys(maxWait=dur, keyList=settings.key_list)

    hit = bool(resp)
    rt = core.getTime() - onset if hit else 0

    # --- Points ---
    if cond == 'win': points = 10 if hit else 0
    elif cond == 'lose': points = 0 if hit else -10
    else: points = 0
    total_points += points

    # --- Feedback ---
    fb_msg = "Hit!" if hit else "Miss!"
    if cond == 'win' and hit: fb_msg += " +10 points"
    elif cond == 'lose' and not hit: fb_msg += " -10 points"
    fb_msg += f"\nTotal: {total_points} points"

    TextStim(win, text=fb_msg, height=0.6, color='black', wrapWidth=25).draw()
    win.flip()
    core.wait(settings.extras.get('feedback_duration', 1.0))

    # --- ITI ---
    TextStim(win, text='+', height=1.0, color='black').draw()
    win.flip()
    core.wait(settings.extras.get('iti_duration', 1.0))

    # --- Update adaptive ---
    step = settings.extras.get('adapt_step', 0.05)
    min_dur = settings.extras.get('min_target_duration', 0.1)
    max_dur = settings.extras.get('max_target_duration', 1.5)
    tracker = target_dur_tracker[cond]
    tracker['total'] += 1
    if hit:
        tracker['hits'] += 1
    rate = tracker['hits'] / tracker['total']
    if rate > 0.66:
        tracker['duration'] = max(tracker['duration'] - step, min_dur)
    elif rate < 0.66:
        tracker['duration'] = min(tracker['duration'] + step, max_dur)

    return {
        'condition': cond,
        'stim': stim_label,
        'response': settings.response_key if hit else 0,
        'rt_ms': int(rt * 1000),
        'points': points,
        'hit': hit,
        'target_duration': dur
    }, total_points
