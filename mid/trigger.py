from typing import Callable, Any, Optional, Dict, List

class Trigger:
    """
    Trigger system abstraction. Provides a unified way to send trigger codes to
    external devices (e.g., via parallel port, serial port, or dummy print).
    """
    def __init__(self, trigger_func: Optional[Callable[[int], None]] = None):
        self.trigger_func = trigger_func or (lambda x: print(f"Trigger sent: {x}"))

    def send(self, code: int):
        """Send a trigger code."""
        self.trigger_func(code)