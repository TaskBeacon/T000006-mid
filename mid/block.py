import random
import numpy as np
class Block:
    def __init__(self, block_id, settings, stim_map, window, keyboard, generate_conditions_func, assign_stimuli_func, seed=None):
        self.block_id = block_id
        self.settings = settings
        self.stim_map = stim_map
        self.window = window
        self.kb = keyboard
        self.seed = seed
        self.conditions = generate_conditions_func(settings.trials_per_block, settings.cue_types, seed)
        self.stimuli = assign_stimuli_func(self.conditions, stim_map)
        self.trials = list(zip(self.conditions, self.stimuli))

        self.results = []

    def run(self, run_trial_func):
        for i, (cond, stim) in enumerate(self.trials):
            result = run_trial_func(self.window, self.kb, self.settings, cond, stim)
            result['trial_index'] = i
            result['block_id'] = self.block_id
            result['condition'] = cond
            result['stim'] = stim
            self.results.append(result)



def generate_balanced_conditions(n_trials, condition_labels, seed=None):
    """
    Generates a balanced and shuffled sequence of MID task conditions.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    n_conditions = len(condition_labels)
    trials_per_condition = n_trials // n_conditions
    remainder = n_trials % n_conditions

    # Fill balanced array
    condition_list = []
    for label in condition_labels:
        condition_list.extend([label] * trials_per_condition)

    # If not divisible, randomly add remaining trials
    if remainder > 0:
        extras = random.choices(condition_labels, k=remainder)
        condition_list.extend(extras)

    random.shuffle(condition_list)
    return np.array(condition_list)


def assign_stimuli(conditions, stim_map):
    return np.array([stim_map[c] for c in conditions], dtype=object)
