from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from math import ceil

@dataclass
class TaskSettings:
    # --- Window settings ---
    size: List[int] = field(default_factory=lambda: [1920, 1080])
    monitor: str = 'testMonitor'
    units: str = 'deg'
    screen: int = 1
    bg_color: str = 'white'
    fullscreen: bool = False

    # --- Basic experiment structure ---
    total_blocks: int = 1
    total_trials: int = 10

    # --- Response settings ---
    response_key: str = 'space'
    key_list: List[str] = field(default_factory=lambda: ['space'])

    # --- Trial logic ---
    cue_types: List[str] = field(default_factory=lambda: [])
    block_seed: Optional[List[int]] = None

    # --- Computed or optional values ---
    trials_per_block: int = field(init=False)
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.trials_per_block = ceil(self.total_trials / self.total_blocks)
        if not self.block_seed:
            self.block_seed = [None] * self.total_blocks

    @classmethod
    def from_dict(cls, config: dict):
        # Separate known fields from extras
        known_keys = set(f.name for f in cls.__dataclass_fields__.values())
        init_args = {k: v for k, v in config.items() if k in known_keys}
        extras = {k: v for k, v in config.items() if k not in known_keys}
        settings = cls(**init_args)
        settings.extras.update(extras)
        return settings
