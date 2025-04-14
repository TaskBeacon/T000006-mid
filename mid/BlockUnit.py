import numpy as np
from typing import Callable, Any, List, Dict, Optional, Tuple
from psychopy import core, logging


class BlockUnit:
    """
    A flexible and modular block container for trial execution and management.
    """

    def __init__(
        self,
        block_id: str,
        settings: Any,
        stim_map: Optional[Dict[str, Any]] = None,
        window: Any = None,
        keyboard: Any = None,
        seed: Optional[int] = None
    ):
        self.block_id = block_id
        self.settings = settings
        self.win = window
        self.kb = keyboard
        self.seed = seed
        self.stim_map = stim_map or {}

        self.conditions: Optional[np.ndarray] = None
        self.stimuli: Optional[np.ndarray] = None
        self.trials: List[Tuple[Any, Any]] = []

        self.results: List[Dict[str, Any]] = []
        self.meta: Dict[str, Any] = {}

        self._on_start: List[Callable[['BlockUnit'], None]] = []
        self._on_end: List[Callable[['BlockUnit'], None]] = []

    # ----------------------------
    # Chainable Setup
    # ----------------------------

    def generate_conditions(
        self,
        func: Callable[[int, List[str], Optional[int]], np.ndarray],
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[str]] = None
    ):
        n = n_trials or getattr(self.settings, "trials_per_block", 20)
        labels = condition_labels or getattr(self.settings, "conditions", ["A", "B", "C"])
        self.conditions = func(n, labels, seed=self.seed)
        return self

    def assign_stimuli(self, func: Callable[[np.ndarray, Dict[str, Any]], np.ndarray]):
        if self.conditions is None:
            raise ValueError("Must generate conditions before assigning stimuli.")
        self.stimuli = func(self.conditions, self.stim_map)
        self.trials = list(zip(self.conditions, self.stimuli))
        return self

    def generate_stim_sequence(
        self,
        generate_func: Callable,
        assign_func: Callable,
        n_trials: Optional[int] = None,
        condition_labels: Optional[List[str]] = None
    ):
        """Chain wrapper for generating + assigning stimuli"""
        return self.generate_conditions(generate_func, n_trials, condition_labels).assign_stimuli(assign_func)

    def with_trials(self, trial_list: List[Tuple[Any, Any]]):
        """Set custom condition-stimulus pairs directly."""
        self.trials = trial_list
        return self

    # ----------------------------
    # Hooks
    # ----------------------------

    def on_start(self, func: Callable[['BlockUnit'], None]):
        self._on_start.append(func)
        return self

    def on_end(self, func: Callable[['BlockUnit'], None]):
        self._on_end.append(func)
        return self

    # ----------------------------
    # Core Execution
    # ----------------------------

    def run(self, run_trial_func: Callable):
        self.meta['block_start_time'] = core.getAbsTime()
        logging.exp(f"📦 Starting BlockUnit: {self.block_id}")

        for hook in self._on_start:
            hook(self)

        for i, (cond, stim) in enumerate(self.trials):
            result = run_trial_func(
                self.win, self.kb, self.settings, cond, stim
            )
            result.update({
                "trial_index": i,
                "block_id": self.block_id,
                "condition": cond,
                "stim_label": getattr(stim, 'name', str(stim))
            })
            self.results.append(result)

        for hook in self._on_end:
            hook(self)

        self.meta['block_end_time'] = core.getAbsTime()
        self.meta['duration'] = self.meta['block_end_time'] - self.meta['block_start_time']
        logging.exp(f"✅ Finished BlockUnit '{self.block_id}' in {self.meta['duration']:.2f}s")

    def to_dict(self) -> List[Dict[str, Any]]:
        return self.results

    def __len__(self):
        return len(self.trials)

    def describe(self):
        cue_summary = {c: list(self.conditions).count(c) for c in set(self.conditions)} if self.conditions is not None else {}
        print(f"🧱 BlockUnit '{self.block_id}' — {len(self.trials)} trials")
        print(f"  Cue Distribution: {cue_summary}")

def generate_balanced_conditions(n_trials, condition_labels, seed=None):
    if seed is not None:
        np.random.seed(seed)
    n_per_cond = n_trials // len(condition_labels)
    extra = n_trials % len(condition_labels)
    conditions = condition_labels * n_per_cond + list(np.random.choice(condition_labels, extra))
    np.random.shuffle(conditions)
    return np.array(conditions)

def assign_stimuli(conditions, stim_map):
    return np.array([stim_map[f"cue_{c}"] for c in conditions], dtype=object)
