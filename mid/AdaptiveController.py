from typing import Dict, List, Optional
from psychopy import logging


class AdaptiveController:
    """
    AdaptiveController dynamically adjusts stimulus duration based on participant performance,
    aiming to maintain a target accuracy rate (e.g., 66%).

    It supports both general (pooled) or condition-specific tracking,
    and is suitable for use across multiple blocks of trials.

    Attributes:
    -----------
    default_duration : float
        Starting stimulus duration (in seconds).
    min_duration : float
        Minimum allowed duration for the stimulus.
    max_duration : float
        Maximum allowed duration for the stimulus.
    step : float
        Amount to increase/decrease duration based on performance.
    target_accuracy : float
        Desired hit rate (0.0 to 1.0).
    condition_specific : bool
        Whether to track adjustments separately for each condition.
    enable_logging : bool
        If True, log changes via PsychoPy's `logging.data`.
    """

    def __init__(
        self,
        initial_duration: float = 0.4,
        min_duration: float = 0.1,
        max_duration: float = 1.0,
        step: float = 0.02,
        target_accuracy: float = 0.66,
        condition_specific: bool = False,
        enable_logging: bool = True
    ):
        """
        Initialize the adaptive controller.

        Parameters
        ----------
        initial_duration : float
            The starting stimulus duration.
        min_duration : float
            The shortest allowed stimulus duration.
        max_duration : float
            The longest allowed stimulus duration.
        step : float
            The adjustment step for each trial.
        target_accuracy : float
            The desired accuracy to maintain.
        condition_specific : bool
            Whether to track each condition separately.
        enable_logging : bool
            If True, logs updates via `logging.data()`.
        """
        self.default_duration = initial_duration
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.step = step
        self.target_accuracy = target_accuracy
        self.condition_specific = condition_specific
        self.enable_logging = enable_logging

        self.durations: Dict[Optional[str], float] = {}
        self.histories: Dict[Optional[str], List[bool]] = {}

    def _get_key(self, condition: Optional[str]) -> Optional[str]:
        """
        Internal helper to determine the key for condition-based tracking.
        """
        return condition if self.condition_specific else None

    def update(self, hit: bool, condition: Optional[str] = None):
        """
        Update internal state based on the latest trial outcome.

        Parameters
        ----------
        hit : bool
            Whether the participant successfully responded.
        condition : str or None
            The condition label associated with the trial (if using condition-specific tracking).
        """
        key = self._get_key(condition)

        if key not in self.durations:
            self.durations[key] = self.default_duration
            self.histories[key] = []

        self.histories[key].append(hit)
        acc = sum(self.histories[key]) / len(self.histories[key])

        old_duration = self.durations[key]
        if acc > self.target_accuracy:
            new_duration = max(self.min_duration, old_duration - self.step)
        else:
            new_duration = min(self.max_duration, old_duration + self.step)

        self.durations[key] = new_duration

        if self.enable_logging:
            label = f"[{condition}]" if condition else ""
            logging.data(f"🎯 Adaptive{label} — Trials: {len(self.histories[key])}, "
                        f"Accuracy: {acc:.2%}, Duration updated: {old_duration:.3f} → {new_duration:.3f}")

    def get_duration(self, condition: Optional[str] = None) -> float:
        """
        Get the current stimulus duration to use for a given condition.

        Parameters
        ----------
        condition : str or None
            The condition to fetch the duration for (if using condition-specific tracking).

        Returns
        -------
        float
            The duration to use for the next stimulus.
        """
        key = self._get_key(condition)
        return self.durations.get(key, self.default_duration)

    def describe(self):
        """
        Print a human-readable summary of controller state and accuracy per condition.
        """
        print("📊 Adaptive Controller Status")
        for key, history in self.histories.items():
            label = f"[{key}]" if key else "[All]"
            acc = sum(history) / len(history)
            print(f"  {label} — Accuracy: {acc:.2%} ({len(history)} trials), Duration: {self.durations[key]:.3f}")
