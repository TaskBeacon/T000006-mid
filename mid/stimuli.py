from psychopy import core, visual, logging
from psychopy.hardware.keyboard import Keyboard
from typing import Callable, Any, Optional, Dict, List
import random

class StimUnit:
    """
    A modular stimulus unit for PsychoPy, supporting stimulus display, triggers,
    responses, time-locked logging, and lifecycle hooks.
    """
    def __init__(self, win: visual.Window, trigger: Optional[Any] = None):
        self.win = win
        self.trigger = trigger or (lambda code: print(f"Trigger sent: {code}"))
        self.stimuli: List[visual.BaseVisualStim] = []
        self.state: Dict[str, Any] = {}
        self.clock = core.Clock()
        self.keyboard = Keyboard()
        self._hooks: Dict[str, List] = {"start": [], "response": [], "timeout": [], "end": []}

    def add_stim(self, stim: visual.BaseVisualStim):
        self.stimuli.append(stim)
        return self

    def set_state(self, **kwargs):
        self.state.update(kwargs)

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.state)

    def send_trigger(self, trigger_code: int):
        self.trigger.send(trigger_code)
        return self

    def log_unit(self):
        logging.data(f"StimUnit Data: {self.state}")

    def on_start(self, func: Optional[Callable[['StimUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["start"].append(f)
                return self
            return decorator
        else:
            self._hooks["start"].append(func)
            return self

    def on_response(self, keys: List[str], func: Optional[Callable[['StimUnit', str, float], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["response"].append((keys, f))
                return self
            return decorator
        else:
            self._hooks["response"].append((keys, func))
            return self

    def on_timeout(self, timeout: float, func: Optional[Callable[['StimUnit'], None]] = None):
        if func is None:
            def decorator(f):
                self._hooks["timeout"].append((timeout, f))
                return self
            return decorator
        else:
            self._hooks["timeout"].append((timeout, func))
            return self

    def on_end(self, func: Optional[Callable[['StimUnit'], None]] = None):
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

        def auto_close(unit: 'StimUnit'):
            unit.set_state(
                duration=t_val,
                timeout_triggered=True,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_timeout(t_val, auto_close)

    def close_on(self, *keys: str):
        """Close on specific key press (no trigger support)."""
        def close_fn(unit: 'StimUnit', key: str, rt: float):
            unit.set_state(
                keys=key,
                response_time=rt,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
        return self.on_response(list(keys), close_fn)

    def show(self, duration: float | tuple[float, float], trigger_onset: int = 0):
        """
        Show static stimulus for a fixed or jittered duration.
        Flip-synced trigger, onset/offset logging.
        """
        t_val = random.uniform(*duration) if isinstance(duration, tuple) else duration
        self.set_state(duration=t_val)

        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, trigger_onset)
        flip_time = self.win.flip()

        self.set_state(
            onset_time=flip_time,
            onset_time_global=core.getAbsTime(),
            trigger=trigger_onset
        )

        self.clock.reset()
        while self.clock.getTime() < t_val:
            for stim in self.stimuli:
                stim.draw()
            self.win.flip()

        self.set_state(
            close_time=core.getTime(),
            close_time_global=core.getAbsTime()
        )
        self.log_unit()
        return self

    def capture_response(
        self,
        keys: list[str],
        duration: float,
        trigger_onset: int = 0,
        trigger_response: int | dict[str, int] = 1,
        trigger_timeout: int = 99
    ):
        """
        Wait for a keypress or timeout. Triggers and onset time synced to visual flip.
        """
        for stim in self.stimuli:
            stim.draw()
        self.win.callOnFlip(self.send_trigger, trigger_onset)
        flip_time = self.win.flip()

        self.set_state(
            onset_time=flip_time,
            onset_time_global=core.getAbsTime()
        )

        self.clock.reset()
        responded = False
        while not responded and self.clock.getTime() < duration:
            for stim in self.stimuli:
                stim.draw()
            self.win.flip()

            keypress = self.keyboard.getKeys(keyList=keys, timeStamped=self.clock)
            if keypress:
                k, rt = keypress[0].name, keypress[0].rt
                self.set_state(
                    hit=True, response=k, rt=rt,
                    close_time=core.getTime(),
                    close_time_global=core.getAbsTime()
                )

                if isinstance(trigger_response, dict):
                    self.send_trigger(trigger_response.get(k, 1))
                else:
                    self.send_trigger(trigger_response)

                responded = True
                break

        if not responded:
            self.set_state(
                hit=False, response=None, rt=0.0,
                close_time=core.getTime(),
                close_time_global=core.getAbsTime()
            )
            self.send_trigger(trigger_timeout)

        self.log_unit()
        return self

    def run(self):
        """
        Full logic loop for displaying stimulus, collecting response, handling timeout,
        and logging with precision timing.
        """
        self.set_state(global_time=core.getAbsTime())

        for hook in self._hooks["start"]:
            hook(self)

        for stim in self.stimuli:
            stim.draw()
        flip_time = self.win.flip()

        self.set_state(
            onset_time=flip_time,
            onset_time_global=core.getAbsTime()
        )
        self.clock.reset()

        responded = False
        while not responded:
            for stim in self.stimuli:
                stim.draw()
            self.win.flip()

            keys = self.keyboard.getKeys(timeStamped=self.clock)
            if keys:
                for key_obj in keys:
                    key_name, key_rt = key_obj.name, key_obj.rt
                    for valid_keys, hook in self._hooks["response"]:
                        if key_name in valid_keys:
                            responded = True
                            hook(self, key_name, key_rt)
                            break
                    if responded:
                        break

            elapsed = self.clock.getTime()
            for timeout_duration, timeout_hook in self._hooks["timeout"]:
                if elapsed >= timeout_duration and not responded:
                    responded = True
                    self.set_state(
                        timeout_triggered=True,
                        duration=elapsed,
                        close_time=core.getTime(),
                        close_time_global=core.getAbsTime()
                    )
                    timeout_hook(self)
                    break

        self.set_state(
            close_time=core.getTime(),
            close_time_global=core.getAbsTime()
        )
        for hook in self._hooks["end"]:
            hook(self)
        self.log_unit()
