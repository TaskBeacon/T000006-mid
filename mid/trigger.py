from typing import Callable, Optional, Union
from psychopy import logging, core
from dataclasses import dataclass, field
from typing import Dict, Union
import yaml

class TriggerSender:
    """
    Generalized trigger sender. User provides the actual send function.

    Usage:
    >>> Trigger(lambda code: ser.write(bytes([code])))
    >>> Trigger(mock=True)  # For development/logging only
    """

    def __init__(
        self,
        trigger_func: Optional[Callable[[int], None]] = None,
        *,
        mock: bool = False,
        post_delay: float = 0.001,
        on_trigger_start: Optional[Callable[[], None]] = None,
        on_trigger_end: Optional[Callable[[], None]] = None,
    ):
        """
        Parameters:
        - trigger_func: The actual function to send the trigger (int -> None).
        - mock: If True, overrides with a mock print trigger.
        - post_delay: Time in seconds to wait after sending trigger (default 1ms).
        - on_trigger_start: Optional callable to be called before each trigger (e.g., port open).
        - on_trigger_end: Optional callable to be called after each trigger (e.g., port close).
        """
        if mock or trigger_func is None:
            self.trigger_func = lambda code: print(f"[MockTrigger] Sent code: {code}")
        else:
            self.trigger_func = trigger_func

        self.post_delay = post_delay
        self.on_trigger_start = on_trigger_start
        self.on_trigger_end = on_trigger_end

    def send(self, code: int):
        """Send a trigger code."""
        if self.on_trigger_start:
            self.on_trigger_start()

        self.trigger_func(code)

        if self.post_delay:
            core.wait(self.post_delay)

        if self.on_trigger_end:
            self.on_trigger_end()

        logging.data(f"Trigger sent: {code}")


# def send_serial_trigger(
#     port: str = "COM3",
#     baudrate: int = 115200,
# ) -> Callable[[int], None]:
#     """
#     Returns a trigger function that sends codes over serial port.

#     Parameters:
#     - port: Serial port name (e.g., "COM3" or "/dev/ttyUSB0")
#     - baudrate: Baud rate for serial communication
#     Returns:
#     - A function that takes a code (int) and sends it via serial
#     """
#     import serial
#     ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)
#     return lambda code: ser.write(bytes(code))

    

# def send_lpt_trigger(address: int = 0x0378) -> Callable[[int], None]:
#     """
#     Returns a trigger function that sends codes over parallel port.

#     Parameters:
#     - address: LPT port base address (default is 0x0378)

#     Returns:
#     - A function that takes a code (int) and sends it via LPT
#     """
#     try:
#         from psychopy import parallel
#         port = parallel.ParallelPort(address=address)
#         return lambda code: port.setData(code)
#     except Exception as e:
#         print(f"[LPT Trigger Error] Falling back to mock: {e}")
#         return lambda code: print(f"[Fallback LPT Trigger] Sent code: {code}")


def show_ports():
    """
    List all available serial ports with descriptions.
    """
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for i, p in enumerate(ports):
            print(f"[{i}] {p.device} - {p.description}")



@dataclass
class TriggerBank:
    triggers: Dict[str, int] = field(default_factory=dict)

    def get(self, event: str) -> Union[int, None]:
        """Get the trigger code (0–255) for a given event."""
        return self.triggers.get(event, None)

    def add(self, event: str, code: int):
        """Add a single event-code pair."""
        if not isinstance(code, int) or not (0 <= code <= 255):
            raise ValueError(f"Trigger code must be an int in range 0–255. Got: {code}")
        self.triggers[event] = code

    def add_from_dict(self, trigger_map: Dict[str, Union[int, list]]):
        """Add multiple event-code mappings from a dictionary."""
        for event, code in trigger_map.items():
            if isinstance(code, int):
                self.add(event, code)
            elif isinstance(code, list) and len(code) == 1 and isinstance(code[0], int):
                self.add(event, code[0])  # support list format like: key: [33]
            else:
                raise ValueError(f"Invalid code for event '{event}': {code}")

    def add_from_yaml(self, yaml_path: str):
        """Load triggers from a YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        triggers = data.get("triggers", {})
        self.add_from_dict(triggers)
