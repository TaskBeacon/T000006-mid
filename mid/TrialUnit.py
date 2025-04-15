from psychopy import core, visual, event, logging
from psychopy.hardware.keyboard import Keyboard
from typing import Callable, Optional, List, Dict, Any, Union
import random
from mid.Trigger import Trigger

class TrialUnit:
    """
    A modular Trial unit for PsychoPy, supporting stimulus display, triggers,
    responses, time-locked logging, and lifecycle hooks.
    """

    def __init__(self, win: visual.Window, trigger: Optional[Trigger] = None, frame_time_seconds: float = 1/60):
        self.win = win
        self.trigger = trigger or Trigger()
        self.stimuli: List[visual.BaseVisualStim] = []
        self.state: Dict[str, Any] = {}
        self.clock = core.Clock()
        self.keyboard = Keyboard()
        self._hooks: Dict[str, List] = {"start": [], "response": [], "timeout": [], "end": []}
        self.frame_time_seconds = frame_time_seconds

    def add_stim(self, stim: visual.BaseVisualStim) -> "TrialUnit":
        self.stimuli.append(stim)
        return self

    def clear_stimuli(self) -> "TrialUnit":
        """Remove all previously added stimuli (e.g., between blocks)."""
        self.stimuli.clear()
        return self

    def set_state(self, **kwargs) -> None:
        self.state.update(kwargs)

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.state)

    def send_trigger(self, trigger_code: int) -> "TrialUnit":
        self.trigger.send(trigger_code)
        return self

    def log_unit(self) -> None:
        logging.data(f"TrialUnit Data: {self.state}")

    def describe_state(self) -> None:
        """Print the current state for inspection."""
        print("TrialUnit State")
        for k, v in self.state.items():
            print(f"  {k}: {v}")

    def simulate_response(self, key: str, rt: float) -> None:
        """Set a fake response (e.g., for testing)."""
        self.set_state(
            response=key,
            rt=rt,
            hit=True,
            close_time=core.getTime(),
            close_time_global=core.getAbsTime()
        )

    def on_start(self, func: Optional[Callable[['TrialUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["start"].append(f)
                return self
            return decorator
        else:
            self._hooks["start"].append(func)
            return self

    def on_response(self, keys: List[str], func: Optional[Callable[['TrialUnit', str, float], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["response"].append((keys, f))
                return self
            return decorator
        else:
            self._hooks["response"].append((keys, func))
            return self

    def on_timeout(self, timeout: float, func: Optional[Callable[['TrialUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["timeout"].append((timeout, f))
                return self
            return decorator
        else:
            self._hooks["timeout"].append((timeout, func))
            return self

    def on_end(self, func: Optional[Callable[['TrialUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["end"].append(f)
                return self
            return decorator
        else:
            self._hooks["end"].append(func)
            return self

    def duration(self, t: float | tuple[float, float]):
        """Auto-close after a fixed or jittered duration (no trigger support)."""
        t_val = random.uniform(*t) if isinstance(t, tuple) else t

        def auto_close(unit: 'TrialUnit'):
            unit.set_state(
                duration=t_val,
                timeout_triggered=True,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_timeout(t_val, auto_close)

    def close_on(self, *keys: str):
        """Close on specific key press (no trigger support)."""
        def close_fn(unit: 'TrialUnit', key: str, rt: float):
            unit.set_state(
                keys=key,
                response_time=rt,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_response(list(keys), close_fn)


    def capture_response(
        self,
        keys: list[str],
        duration: float,
        onset_trigger: int = 0,
        response_trigger: int | dict[str, int] = 1,
        timeout_trigger: int = 99
    ) -> "TrialUnit":
        """
        Wait for a keypress or timeout. Triggers and onset time synced to visual flip.
        """
        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        flip_time = self.win.flip()

        self.set_state(
            onset_time=flip_time,
            onset_time_global=core.getAbsTime()
        )

        self.clock.reset()
        self.keyboard.clearEvents()
        responded = False
        while not responded and self.clock.getTime() < duration:
            for stim in self.stimuli:
                stim.draw()
            self.win.flip()
            keypress = self.keyboard.getKeys(keyList=keys, waitRelease=False)
            if keypress:
                k, rt = keypress[0].name, keypress[0].rt
                self.set_state(
                    hit=True, response=k, rt=rt,
                    close_time=core.getTime(),
                    close_time_global=core.getAbsTime()
                )

                if isinstance(response_trigger, dict):
                    self.send_trigger(response_trigger.get(k, 1))
                else:
                    self.send_trigger(response_trigger)

                responded = True
                break

        if not responded:
            self.set_state(
                hit=False, response=None, rt=0.0,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
            self.send_trigger(timeout_trigger)

        self.log_unit()
        return self

    def run(self, frame_based: bool = False) -> "TrialUnit":
        """
        Full logic loop for displaying stimulus, collecting response, handling timeout,
        and logging with precision timing.

        Parameters:
        -----------
        frame_based : bool
            Whether to use frame-counted duration instead of time-based duration.
        """
        self.set_state(global_time=core.getAbsTime())

        for hook in self._hooks["start"]:
            hook(self)

        # Initial flip with onset timestamp
        for stim in self.stimuli:
            stim.draw()
        flip_time = self.win.flip()

        self.set_state(
            onset_time=self.clock.getTime(),
            flip_time=flip_time,
            onset_time_global=core.getAbsTime()
        )

        self.clock.reset()
        self.keyboard.clearEvents()
        self.keyboard.clearEvents()
        responded = False

        all_keys = list(set(k for k_list, _ in self._hooks["response"] for k in k_list))

        if frame_based:
            # Estimate total frame duration based on maximum timeout
            max_timeout = max((t for t, _ in self._hooks["timeout"]), default=5.0)
            n_frames = int(round(max_timeout / self.frame_time_seconds))

            for _ in range(n_frames):
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

                keys = self.keyboard.getKeys(keyList=all_keys, waitRelease=False)
                for key_obj in keys:
                    key_name, key_rt = key_obj.name, key_obj.rt
                    for valid_keys, hook in self._hooks["response"]:
                        if key_name in valid_keys:
                            hook(self, key_name, key_rt)
                            responded = True
                            break
                    if responded:
                        break

                elapsed = self.clock.getTime()
                for timeout_duration, timeout_hook in self._hooks["timeout"]:
                    if elapsed >= timeout_duration and not responded:
                        self.set_state(
                            timeout_triggered=True,
                            duration=elapsed,
                            close_time=core.getTime(),
                            close_time_global=core.getAbsTime()
                        )
                        timeout_hook(self)
                        responded = True
                        break
                if responded:
                    break
        else:
            # Time-based loop
            while not responded:
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

                keys = self.keyboard.getKeys(keyList=all_keys, waitRelease=False)
                for key_obj in keys:
                    key_name, key_rt = key_obj.name, key_obj.rt
                    for valid_keys, hook in self._hooks["response"]:
                        if key_name in valid_keys:
                            hook(self, key_name, key_rt)
                            responded = True
                            break
                    if responded:
                        break

                elapsed = self.clock.getTime()
                for timeout_duration, timeout_hook in self._hooks["timeout"]:
                    if elapsed >= timeout_duration and not responded:
                        self.set_state(
                            timeout_triggered=True,
                            duration=elapsed,
                            close_time=core.getTime(),
                            close_time_global=core.getAbsTime()
                        )
                        timeout_hook(self)
                        responded = True
                        break

        self.set_state(
            close_time=core.getTime(),
            close_time_global=core.getAbsTime()
        )
        for hook in self._hooks["end"]:
            hook(self)

        self.log_unit()
        return self

    
    def show(
        self,
        duration: float | list,
        onset_trigger: int = 0,
        frame_based: bool = True
    ) -> "TrialUnit":
        """
        Display the stimulus for a specified duration, either using frame-based timing
        (recommended for EEG/fMRI) or precise time-based loop.
        """
        local_rng = random.Random()
        t_val = local_rng.uniform(*duration) if isinstance(duration, list) else duration
        self.set_state(duration=t_val)

        # --- Initial Flip (trigger locked to onset) ---
        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        flip_time = self.win.flip(clearBuffer=True)  # clear to avoid flickering

        self.set_state(
            onset_time=self.clock.getTime(),
            flip_time=flip_time,
            onset_time_global=core.getAbsTime(),
            onset_trigger=onset_trigger
        )

        # --- Frame-based or precise timing ---
        tclock = core.Clock()
        tclock.reset()

        if frame_based:
            n_frames = int(round(t_val / self.frame_time_seconds))
            for _ in range(n_frames):
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()
        else:
            while tclock.getTime() < t_val:
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

        self.set_state(
            close_time=self.clock.getTime(),
            close_time_global=core.getAbsTime()
        )
        self.log_unit()
        return self

    def capture_response(
        self,
        keys: list[str],
        duration: float | list,
        onset_trigger: int = 0,
        response_trigger: int | dict[str, int] = 1,
        timeout_trigger: int = 99,
        frame_based: bool = True
    ) -> "TrialUnit":
        """
        Wait for a keypress or timeout. Supports both time-based and frame-based duration.
        Triggers and onset time synced to visual flip.

        Parameters
        ----------
        keys : list[str]
            Keys to listen for.
        duration : float
            Response window duration in seconds.
        onset_trigger : int
            Trigger code sent at stimulus onset.
        response_trigger : int | dict[str, int]
            Trigger code for response, can be per-key.
        timeout_trigger : int
            Trigger code for timeout.
        frame_based : bool
            Whether to use frame counting instead of time-based control.
        """
        local_rng = random.Random()
        t_val = local_rng.uniform(*duration) if isinstance(duration, list) else duration
        self.set_state(duration=t_val)

        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, onset_trigger)
        flip_time = self.win.flip()

        self.set_state(
            onset_time=self.clock.getTime(),
            flip_time=flip_time,
            onset_time_global=core.getAbsTime(),
            onset_trigger=onset_trigger
        )

        self.clock.reset()
        self.keyboard.clearEvents()
        responded = False

        if frame_based:
            n_frames = int(round(t_val / self.frame_time_seconds))
            for _ in range(n_frames):
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

                keypress = self.keyboard.getKeys(keyList=keys, waitRelease=False)
                if keypress:
                    k= keypress[0].name
                    rt = self.clock.getTime()
                    self.set_state(
                        hit=True, 
                        response=k, 
                        rt=rt,
                        close_time=self.clock.getTime(),
                        close_time_global=core.getAbsTime()
                    )

                    response_trigger = response_trigger.get(k, 1) if isinstance(response_trigger, dict) else response_trigger
                    self.send_trigger(response_trigger)
                    self.set_state(response_trigger=response_trigger)
                    responded = True
                    break
        else:

            while not responded and self.clock.getTime() < duration:
                for stim in self.stimuli:
                    stim.draw()
                self.win.flip()

                keypress = self.keyboard.getKeys(keyList=keys, waitRelease=False)
                if keypress:
                    k = keypress[0].name
                    rt = self.clock.getTime()
                    self.set_state(
                        hit=True, response=k, rt=rt,
                        close_time=self.clock.getTime(),
                        close_time_global=core.getAbsTime()
                    )

                    response_trigger = response_trigger.get(k, 1) if isinstance(response_trigger, dict) else response_trigger
                    self.send_trigger(response_trigger)
                    self.set_state(response_trigger=response_trigger)
                    responded = True
                    break


        if not responded:
            self.set_state(
                hit=False, 
                response=None, 
                rt=0.0,
                close_time=self.clock.getTime(),
                close_time_global=core.getAbsTime(),
                timeout_trigger=timeout_trigger
            )
            self.send_trigger(timeout_trigger)

        self.log_unit()
        return self



