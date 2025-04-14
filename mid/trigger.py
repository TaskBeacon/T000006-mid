from typing import Callable, Optional, Union
from psychopy import logging

class Trigger:
    """
    Flexible trigger sender for EEG, fMRI, or development.

    Usage:
    - Trigger("eeg")
    - Trigger("fmri")
    - Trigger(lambda x: ...)
    """

    def __init__(self, mode: Union[str, Callable[[int], None], None] = None):
        if callable(mode):
            self.trigger_func = mode
        elif isinstance(mode, str):
            mode = mode.lower()
            if mode == "eeg":
                self.trigger_func = self._eeg_trigger()
            elif mode == "fmri":
                self.trigger_func = self._fmri_trigger()
            elif mode == "mock" or mode == "dev":
                self.trigger_func = lambda code: print(f"[MockTrigger] Sent code: {code}")
            else:
                raise ValueError(f"Unknown trigger mode: {mode}")
        else:
            self.trigger_func = lambda code: print(f"[MockTrigger] Sent code: {code}")

    def send(self, code: int):
        """Send a trigger code."""
        self.trigger_func(code)
        logging.data(f"🔺 Trigger sent: {code}")

    def _eeg_trigger(self) -> Callable[[int], None]:
        """
        Returns a trigger function for EEG via parallel port.
        Requires pyparallel or psychopy.parallel.
        """
        try:
            from psychopy import parallel
            port = parallel.ParallelPort()
            return lambda code: port.setData(code)
        except Exception as e:
            print(f"[EEG Trigger Error] Falling back to mock: {e}")
            return lambda code: print(f"[Fallback EEG Trigger] Sent code: {code}")

    def _fmri_trigger(self) -> Callable[[int], None]:
        """
        Returns a trigger function for fMRI (typically sending a character via serial).
        """
        try:
            import serial
            ser = serial.Serial('COM1', baudrate=115200, timeout=0.1)  # Adjust port/baudrate
            return lambda code: ser.write(bytes([code]))
        except Exception as e:
            print(f"[fMRI Trigger Error] Falling back to mock: {e}")
            return lambda code: print(f"[Fallback fMRI Trigger] Sent code: {code}")
