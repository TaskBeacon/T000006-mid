import numpy as np

def get_mid_feedback(results, block_id):
    """
    Generate block-level feedback for MID task.
    
    Parameters
    ----------
    results : list of dict
        List of trial results for the block.
    block_id : int
        The current block number.

    Returns
    -------
    str : formatted feedback message.
    dict : performance summary (optional, if needed elsewhere).
    """
    rt_vals = [r['rt_ms'] for r in results if r['response'] != 0]
    accuracy = np.mean([1 if r['response'] != 0 else 0 for r in results]) * 100
    mean_rt = np.mean(rt_vals) if rt_vals else 0
    block_points = sum([r.get('points', 0) for r in results])

    summary = {
        "block": block_id,
        "mean_rt": mean_rt,
        "accuracy": accuracy,
        "points": block_points
    }

    feedback_text = (
        f"End of Block #{block_id}\n"
        f"Mean RT: {mean_rt:.0f} ms\n"
        f"Accuracy: {accuracy:.1f}%\n"
        f"Block Points: {block_points}\n"
        "Press SPACE to continue..."
    )

    return feedback_text, summary
