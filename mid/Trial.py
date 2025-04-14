from psychopy import core, logging
from typing import Callable, Any, Optional, Dict, List
from .TrialUnit import TrialUnit
class Trial:
    """
    A container for sequencing multiple TrialUnits as a single experimental trial.
    Handles trial-level hooks, data aggregation, and logging.
    """

    def __init__(self, name: str = "", units: Optional[List[TrialUnit]] = None):
        self.name = name
        self.units: List[TrialUnit] = units or []
        self.trial_state: Dict[str, Any] = {}
        self._start_hooks: List[Callable[['Trial'], None]] = []
        self._end_hooks: List[Callable[['Trial'], None]] = []

    def add_unit(self, unit: TrialUnit):
        """Add a TrialUnit to this trial."""
        self.units.append(unit)
        return self

    def on_start(self, func: Callable[['Trial'], None]):
        """Register a function to run before the trial starts."""
        self._start_hooks.append(func)
        return self

    def on_end(self, func: Callable[['Trial'], None]):
        """Register a function to run after the trial ends."""
        self._end_hooks.append(func)
        return self

    def set_state(self, **kwargs):
        """Update trial-level state."""
        self.trial_state.update(kwargs)

    def get_state(self, key: str, default=None):
        return self.trial_state.get(key, default)

    def run(self):
        """Run all TrialUnits in sequence and log aggregate state."""
        logging.exp(f"Running trial: {self.name}")
        self.set_state(trial_name=self.name, trial_start=core.getAbsTime())

        for hook in self._start_hooks:
            hook(self)

        for unit in self.units:
            unit.run()
            self.trial_state.update(unit.to_dict())  # merge unit state

        self.set_state(trial_end=core.getAbsTime())

        for hook in self._end_hooks:
            hook(self)

        # Final summary log
        logging.data(f"Trial '{self.name}' data: {self.trial_state}")
        return self

    def to_dict(self):
        """Return final aggregated state."""
        return dict(self.trial_state)
