from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from math import ceil

@dataclass
class TaskSettings:
    """
    Stores all experiment settings for task execution and window setup.

    This class is meant to be loaded from a config dictionary (e.g., parsed from YAML),
    combining common PsychoPy window parameters, task structure, and extras like timing
    or adaptation parameters.

    Attributes
    ----------
    size : list[int]
        Window size in pixels (e.g., [1280, 720]).
    monitor : str
        Name of the monitor profile to use.
    units : str
        Units for PsychoPy window coordinates (e.g., 'deg', 'pix').
    screen : int
        Screen index to display the window.
    bg_color : str
        Background color for the window.
    fullscreen : bool
        Whether to use fullscreen mode.

    total_blocks : int
        Number of blocks in the experiment.
    total_trials : int
        Total number of trials across all blocks.

    response_key : str
        Default response key (e.g., 'space').
    key_list : list[str]
        Valid key list to listen for responses.

    conditions : list[str]
        List of condition labels (e.g., ['win', 'lose', 'neut']).
    block_seed : list[int] or None
        Optional list of seeds for reproducibility per block.

    extras : dict[str, Any]
        Arbitrary additional parameters (e.g., timing, adaptation) from config.

    trials_per_block : int
        Derived field calculated as total_trials / total_blocks.

    Example
    -------
    >>> import yaml
    >>> with open("config.yaml") as f:
    ...     config = yaml.safe_load(f)
    >>> settings = TaskSettings.from_dict(config['task'])
    >>> print(settings.trials_per_block)
    """
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
    conditions: List[str] = field(default_factory=lambda: [])
    block_seed: Optional[List[int]] = None

    # --- Miscellaneous or task-specific extras ---
    extras: Dict[str, Any] = field(default_factory=dict)

    # --- Computed field ---
    trials_per_block: int = field(init=False)

    def __post_init__(self):
        self.trials_per_block = ceil(self.total_trials / self.total_blocks)
        if not self.block_seed:
            self.block_seed = [None] * self.total_blocks

    @classmethod
    def from_dict(cls, config: dict):
        """
        Load settings from a dictionary (e.g., parsed from YAML).

        Any keys not explicitly defined in the dataclass will be stored in `extras`.

        Parameters
        ----------
        config : dict
            Dictionary of experiment settings.

        Returns
        -------
        TaskSettings
            Configured settings object.
        """
        known_keys = set(f.name for f in cls.__dataclass_fields__.values())
        init_args = {k: v for k, v in config.items() if k in known_keys}
        extras = {k: v for k, v in config.items() if k not in known_keys}
        settings = cls(**init_args)
        settings.extras.update(extras)
        return settings
