from mid.TrialUnit import TrialUnit
def run_mid_trial(win, kb, settings, condition, stim_dict, stim_bank, controller, triggerbank):
    """
    Run a single MID trial sequence (fixation → cue → ITI → target → feedback).
    See full docstring above...
    """
    def make_unit(label: str) -> TrialUnit:
        return TrialUnit(
            win=win,
            unit_label=label,
            frame_time_seconds=settings.frame_time_seconds
        )

    trial_data = {"condition": condition}

    # --- Fixation ---
    make_unit("fixation").add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration, onset_trigger=triggerbank.get("fixation_onset")) \
        .to_dict(trial_data)

    # --- Cue ---
    make_unit("cue").add_stim(stim_dict["cue"]) \
        .show(duration=settings.cue_duration, onset_trigger=triggerbank.get(f"{condition}_cue_onset")) \
        .to_dict(trial_data)


    # --- Anticipation ---
    make_unit("anticipation") \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.anticipation_duration, onset_trigger=triggerbank.get(f"{condition}_anti_onset")) \
        .to_dict(trial_data)

    # --- Target ---
    duration = controller.get_duration(condition)
    target = make_unit("target") \
        .add_stim(stim_dict["target"])
    target.capture_response(
            keys=settings.key_list,
            duration=duration,
            onset_trigger=triggerbank.get(f"{condition}_target_onset"),
            response_trigger=triggerbank.get(f"{condition}_key_press"),
            timeout_trigger=triggerbank.get(f"{condition}_no_response"),
)
    target.to_dict(trial_data)
    

    # --- Feedback ---
    hit = target.get_state("hit", False)
    controller.update(condition, hit)
    if condition == "win":
        delta = 10 if hit else 0
    elif condition == "lose":
        delta = 0 if hit else -10
    else:
        delta = 0

    hit_type = "hit" if hit else "miss"
    fb_stim = stim_bank.get(f"feedback_{condition}_{hit_type}")
    fb = make_unit("feedback") \
        .add_stim(fb_stim) \
        .show(duration=settings.feedback_duration, onset_trigger=triggerbank.get(f"{condition}_{hit_type}_fb_onset"))
    fb.set_state(hit=hit, delta=delta).to_dict(trial_data)
    return trial_data
