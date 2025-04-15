from mid.TrialUnit import TrialUnit
def run_mid_trial(win, kb, settings, condition, stim_dict, stim_bank, controller, fb_manager):
    """
    Run a single MID trial sequence (fixation → cue → ITI → target → feedback).

    Parameters:
    - win: PsychoPy Window
    - kb: PsychoPy Keyboard
    - settings: experimental settings object (must include cue_duration, iti, feedback_duration, response_keys)
    - condition: str, e.g., "win", "lose", "neut"
    - stim_dict: dict with per-trial cue stimuli (e.g., {"cue": ...})
    - stim_bank: instance of StimBank containing shared stimuli
    - controller: AdaptiveController to adjust target duration

    Returns:
    - trial_result: dict containing trial state (hit, rt, response, etc.)
    """

    trial_data = {"condition": condition}

    # --- Fixation ---
    TrialUnit(win).add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration, trigger_onset=11)

    # --- Cue ---
    TrialUnit(win).add_stim(stim_dict["cue"]) \
        .show(duration=settings.cue_duration, trigger_onset=21)

    # --- anticipation ---
    TrialUnit(win).add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.anticipation_duration)

    # --- Target ---
    duration = controller.get_duration(condition)
    target = TrialUnit(win).add_stim(stim_dict['target'])
    target.capture_response(
        keys=settings.key_list,
        duration=duration,
        trigger_onset=31,
        trigger_response=41,
        trigger_timeout=99
    )
    # Update adaptive controller
    controller.update(condition, target.get_state("hit", False))
    trial_data.update(target.to_dict())

    # --- Feedback ---
    delta = fb_manager.update_points(condition, hit=target.get_state("hit", False))
    message = fb_manager.get_message(condition, hit=target.get_state("hit", False), points=abs(delta))

    fb_stim = TextStim(win, text=message, color="white", height=0.08)
    TrialUnit(win).add_stim(fb_stim).show(duration=settings.feedback_duration)

    return trial_data
