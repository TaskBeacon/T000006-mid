from functools import partial

from psyflow import StimUnit, set_trial_context


def _deadline_s(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except Exception:
            return None
    return None


def _next_trial_id(controller) -> int:
    histories = getattr(controller, "histories", {}) or {}
    done = 0
    for items in histories.values():
        try:
            done += len(items)
        except Exception:
            continue
    return int(done) + 1


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """
    Run one MID trial (task-specific phases for responder context).
    """
    trial_id = _next_trial_id(controller)
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    make_unit(unit_label="cue").add_stim(stim_bank.get(f"{condition}_cue")).show(
        duration=settings.cue_duration,
        onset_trigger=settings.triggers.get(f"{condition}_cue_onset"),
    ).to_dict(trial_data)

    anti = make_unit(unit_label="anticipation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        anti,
        trial_id=trial_id,
        phase="anticipation_fixation",
        deadline_s=_deadline_s(settings.anticipation_duration),
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "stage": "anticipation_fixation", "block_idx": block_idx},
        stim_id="fixation",
    )
    anti.capture_response(
        keys=settings.key_list,
        duration=settings.anticipation_duration,
        onset_trigger=settings.triggers.get(f"{condition}_anti_onset"),
        terminate_on_response=False,
    )
    early_response = anti.get_state("response", False)
    anti.set_state(early_response=early_response)
    anti.to_dict(trial_data)

    duration = controller.get_duration(condition)
    target = make_unit(unit_label="target").add_stim(stim_bank.get(f"{condition}_target"))
    set_trial_context(
        target,
        trial_id=trial_id,
        phase="target_response_window",
        deadline_s=_deadline_s(duration),
        valid_keys=list(settings.key_list),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={
            "condition": str(condition),
            "stage": "target_response_window",
            "block_idx": block_idx,
            "target_duration_s": float(duration),
        },
        stim_id=f"{condition}_target",
    )
    target.capture_response(
        keys=settings.key_list,
        duration=duration,
        onset_trigger=settings.triggers.get(f"{condition}_target_onset"),
        response_trigger=settings.triggers.get(f"{condition}_key_press"),
        timeout_trigger=settings.triggers.get(f"{condition}_no_response"),
    )
    target.to_dict(trial_data)

    make_unit(unit_label="prefeedback_fixation").add_stim(stim_bank.get("fixation")).show(
        duration=settings.prefeedback_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    # Early response during the fixation window is always treated as a miss.
    hit = False if early_response else bool(target.get_state("hit", False))
    reward_if_hit = {"win": settings.delta, "lose": 0, "neut": 0}
    penalty_if_miss = {"win": 0, "lose": -settings.delta, "neut": 0}
    delta = reward_if_hit.get(condition, 0) if hit else penalty_if_miss.get(condition, 0)
    controller.update(hit, condition)

    hit_type = "hit" if hit else "miss"
    fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
    fb = make_unit(unit_label="feedback").add_stim(fb_stim).show(
        duration=settings.feedback_duration,
        onset_trigger=settings.triggers.get(f"{condition}_{hit_type}_fb_onset"),
    )
    fb.set_state(hit=hit, delta=delta).to_dict(trial_data)

    return trial_data
