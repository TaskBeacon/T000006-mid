import numpy as np
import random
from types import SimpleNamespace
import warnings

def generate_trial_seq(settings):
    """
    Generates a balanced trial sequence for the MID task.
    Each trial is labeled with:
        - Condition: 'reward', 'punishment', or 'neutral'
        - Stimulus: 'circle', 'square', or 'triangle'
        - Block number and block end flag
    """
    TotalBlocks = settings.TotalBlocks
    TotalTrials = settings.TotalTrials
    TrialsPerBlock = settings.TrialsPerBlock

    ALLconditions = np.empty(TotalTrials, dtype=object)
    ALLstims = np.empty(TotalTrials, dtype=object)
    ALLblocknum = np.zeros(TotalTrials, dtype=int)
    ALLblockEndIdx = np.zeros(TotalTrials, dtype=int)

    # Condition → Stimulus label map
    stim_map = {
        'win': 'circle',
        'lose': 'square',
        'neut': 'triangle',
    }

    for block_i in range(TotalBlocks):
        block_start = block_i * TrialsPerBlock
        block_end = (block_i + 1) * TrialsPerBlock

        blocknum = np.full(TrialsPerBlock, block_i + 1, dtype=int)
        blockEndIdx = np.zeros(TrialsPerBlock, dtype=int)
        blockEndIdx[-1] = 1

        block_seed = None
        if settings.blockSeed is not None:
            block_seed = int(settings.blockSeed[block_i])

        # Step 1: Generate balanced conditions
        conditions = generate_balanced_conditions(
            n_trials=TrialsPerBlock,
            condition_labels=settings.cueTypes,
            seed=block_seed
        )

        # Step 2: Assign stimulus type by condition
        stim_seq = np.array([stim_map[cond] for cond in conditions], dtype=object)

        # Step 3: Store in full arrays
        ALLconditions[block_start:block_end] = conditions
        ALLstims[block_start:block_end] = stim_seq
        ALLblocknum[block_start:block_end] = blocknum
        ALLblockEndIdx[block_start:block_end] = blockEndIdx

    if not (len(ALLconditions) == len(ALLblocknum) == len(ALLstims) == TotalTrials):
        warnings.warn("Trial sequence size mismatch!")

    trialseq = SimpleNamespace()
    trialseq.blocknum = ALLblocknum
    trialseq.BlockEndIdx = ALLblockEndIdx
    trialseq.conditions = ALLconditions
    trialseq.stims = ALLstims

    return trialseq

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
