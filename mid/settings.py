from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from math import ceil

@dataclass
class TaskSettings:
    """
    Stores all experiment settings for task execution and window setup.

    This class is meant to be loaded from a YAML config with nested sections,
    which will be flattened and dynamically promoted to attributes.

    Attributes
    ----------
    # --- Core window and task config ---
    size : list[int]
        Window size in pixels.
    monitor : str
        Monitor profile name.
    units : str
        Units used in PsychoPy (e.g., 'deg', 'pix').
    screen : int
        Display screen index.
    bg_color : str
        Background color of the window.
    fullscreen : bool
        Whether to launch in fullscreen.

    total_blocks : int
        Number of blocks in the experiment.
    total_trials : int
        Total number of trials in the experiment.

    response_key : str
        Default response key (e.g., 'space').
    key_list : list[str]
        List of valid response keys.

    conditions : list[str]
        List of condition labels (e.g., ['win', 'lose', 'neut']).
    block_seed : list[int] or None
        Optional list of per-block seeds.

    trials_per_block : int
        Automatically computed from total_trials / total_blocks.

    ...plus any additional parameters from config, such as:
        - cue_duration
        - iti_duration
        - adapt_step
        - min_target_duration
        - etc.

    Example
    -------
    >>> import yaml
    >>> with open("config.yaml") as f:
    ...     config = yaml.safe_load(f)
    >>> flat_config = {**config['window'], **config['task'], **config['timing']}
    >>> settings = TaskSettings.from_dict(flat_config)
    >>> print(settings.total_blocks)
    >>> print(settings.cue_duration)
    """
    # --- Window settings ---
    size: List[int] = field(default_factory=lambda: [1920, 1080])
    monitor: str = 'testMonitor'
    units: str = 'norm'
    screen: int = 1
    bg_color: str = 'gray'
    fullscreen: bool = True

    # --- Basic experiment structure ---
    total_blocks: int = 1
    total_trials: int = 10

    # --- Response settings ---
    response_key: str = 'space'
    key_list: List[str] = field(default_factory=lambda: ['space'])

    # --- Trial logic ---
    conditions: List[str] = field(default_factory=list)
    block_seed: Optional[List[int]] = None

    # --- Derived fields ---
    trials_per_block: int = field(init=False)


    def __post_init__(self):
        self.trials_per_block = ceil(self.total_trials / self.total_blocks)
        if not self.block_seed:
            self.block_seed = [None] * self.total_blocks
    def __repr__(self):
    # Field Type	Access	Shown in print(settings)
    # Defined in class	✅ settings.total_blocks	✅ yes
    # Added via setattr()	✅ settings.cue_duration	❌ no (unless you override __repr__)
        base = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return f"{self.__class__.__name__}({base})"


    @classmethod
    def from_dict(cls, config: dict):
        """
        Create TaskSettings instance from a flat config dictionary.
        Unknown keys are promoted to attributes on the instance.

        Parameters
        ----------
        config : dict
            Flat dictionary containing both standard and extra keys.

        Returns
        -------
        TaskSettings
        """
        known_keys = set(f.name for f in cls.__dataclass_fields__.values())
        init_args = {k: v for k, v in config.items() if k in known_keys}
        extras = {k: v for k, v in config.items() if k not in known_keys}

        settings = cls(**init_args)
        for k, v in extras.items():
            setattr(settings, k, v)  # promote extras to attributes
        return settings
