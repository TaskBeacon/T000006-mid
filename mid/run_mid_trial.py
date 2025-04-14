from mid.TrialUnit import TrialUnit
from mid.TrialRoutine import TrialRoutine
def run_mid_trial(win, kb, settings, condition, stim, controller):


    routine = TrialRoutine(name=f"MID-{condition}")

    # Fixation Unit
    fix = TrialUnit(win).add_stim(stim_bank.get("fix"))
    fix.show(duration=0.5, trigger_onset=11)
    routine.add_unit(fix)

    # Cue Unit
    cue = TrialUnit(win).add_stim(stim)
    cue.show(duration=settings.cue_duration, trigger_onset=21)
    routine.add_unit(cue)

    # Delay Unit (ITI)
    iti = TrialUnit(win).add_stim(stim_bank.get("blank"))
    iti.show(duration=settings.iti, trigger_onset=0)
    routine.add_unit(iti)

    # Target Unit with adaptive duration
    target_stim = stim_bank.get(f"target_{condition}")
    duration = controller.get_duration(condition)
    target = TrialUnit(win).add_stim(target_stim)
    target.capture_response(
        keys=settings.response_keys,
        duration=duration,
        trigger_onset=31,
        trigger_response=41,
        trigger_timeout=99
    )
    routine.add_unit(target)

    # Feedback Unit
    feedback = TrialUnit(win).add_stim(stim_bank.get("blank"))
    feedback.show(duration=settings.feedback_duration)
    routine.add_unit(feedback)

    # Hook to update controller based on trial outcome
    @target.on_end
    def update_control(u: TrialUnit):
        controller.update(condition, u.get_state("hit", False))

    # Run the routine
    routine.run()
    return routine.to_dict()
