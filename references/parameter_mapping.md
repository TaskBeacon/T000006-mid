# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `conditions` | `task.conditions` | `[win, lose, neut]` | `W2119128116` | Incentive-condition cueing and anticipation are core MID elements. | `source_bound` | Explicit valence/incentive condition split is preserved. |
| `total_blocks` | `task.total_blocks` | `3` | `W2097716692` | Incentive-condition comparisons are estimated over repeated multi-trial runs. | `inferred` | Chosen for stable within-session estimates in EEG context. |
| `total_trials` | `task.total_trials` | `180` | `W2097716692` | Condition-comparable trial counts are required for robust contrasts. | `inferred` | 60 trials/block over 3 blocks. |
| `trial_per_block` | `task.trial_per_block` | `60` | `W2097716692` | Blocked incentive presentation supports manageable participant fatigue and stable estimates. | `inferred` | Matched to `total_trials/total_blocks`. |
| `delta` | `task.delta` | `10` | `W2119128116` | Monetary-incentive framing requires explicit gain/loss magnitude mapping. | `inferred` | Point-value implementation used for operational reward feedback. |
| `cue_duration` | `timing.cue_duration` | `0.3` | `W2119128116` | Brief cue precedes anticipation window in MID state machine. | `inferred` | Maintains clear cue-to-target temporal separation. |
| `anticipation_duration` | `timing.anticipation_duration` | `[1.0, 1.2]` | `W2119128116` | Anticipation interval is explicitly modeled between cue and target onset. | `inferred` | Jittered interval reduces precise expectancy. |
| `feedback_duration` | `timing.feedback_duration` | `1.0` | `W2096412262` | Feedback processing requires explicit post-response outcome display period. | `inferred` | Supports outcome-locked EEG event interpretation. |
| `initial_duration` | `controller.initial_duration` | `0.2` | `W2119128116` | Target detectability is tuned to maintain incentive sensitivity. | `inferred` | Adaptive controller starts at moderate detectability. |
| `min_duration` | `controller.min_duration` | `0.04` | `W2119128116` | Lower bound prevents impossible response windows. | `inferred` | Controller guardrail. |
| `max_duration` | `controller.max_duration` | `0.37` | `W2119128116` | Upper bound prevents trivial target detection. | `inferred` | Controller guardrail. |
| `target_accuracy` | `controller.target_accuracy` | `0.66` | `W2119128116` | MID response windows are often tuned around intermediate hit rates. | `inferred` | Maintains motivational salience across blocks. |
| `*_cue_onset` | `triggers.map.win_cue_onset`, `triggers.map.lose_cue_onset`, `triggers.map.neut_cue_onset` | `10/20/30` | `W2119128116` | Condition-specific cue events are central to anticipation contrasts. | `inferred` | Distinct codes per condition. |
| `*_target_onset` | `triggers.map.win_target_onset`, `triggers.map.lose_target_onset`, `triggers.map.neut_target_onset` | `12/22/32` | `W2119128116` | Target onset is modeled separately from cue/feedback. | `inferred` | Distinct codes per condition. |
| `*_hit_fb_onset` and `*_miss_fb_onset` | `triggers.map.win_hit_fb_onset`, `...` | `13/14`, `23/24`, `33/34` | `W2096412262` | Outcome/feedback event separation is required for feedback-locked analyses. | `inferred` | Hit and miss channels are explicitly separated by condition. |
