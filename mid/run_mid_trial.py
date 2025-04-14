from mid.TrialUnit import TrialUnit
def run_mid_trial(win, kb, settings, condition, stim_dict, stim_bank, controller):
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
    TrialUnit(win).add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.feedback_duration)

    return trial_data
