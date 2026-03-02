# Stimulus Mapping

## Mapping Table

| Condition | Stage/Phase | Stimulus IDs | Participant-Facing Content | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Asset References | Notes |
|---|---|---|---|---|---|---|---|---|
| `win` | `cue -> anticipation_fixation -> target_response_window -> prefeedback_fixation -> feedback` | `win_cue`, `fixation`, `win_target`, `win_hit_feedback`, `win_miss_feedback` | Magenta reward cue, fixation anticipation, black target requiring fast keypress, then reward-contingent hit/miss text feedback. | `W2119128116` | MID reward anticipation structure requires cue-conditioned target response and outcome feedback. | `psychopy_builtin` | `n/a` | Implemented with shape primitives and localized text feedback. |
| `lose` | `cue -> anticipation_fixation -> target_response_window -> prefeedback_fixation -> feedback` | `lose_cue`, `fixation`, `lose_target`, `lose_hit_feedback`, `lose_miss_feedback` | Yellow loss-avoidance cue, fixation anticipation, black target response window, then loss-contingent hit/miss text feedback. | `W2119128116` | MID loss condition parallels reward structure with valence-specific outcomes. | `psychopy_builtin` | `n/a` | Loss feedback magnitude is parameterized by `task.delta`. |
| `neut` | `cue -> anticipation_fixation -> target_response_window -> prefeedback_fixation -> feedback` | `neut_cue`, `fixation`, `neut_target`, `neut_hit_feedback`, `neut_miss_feedback` | Cyan neutral cue, fixation anticipation, black target response window, then neutral hit/miss text feedback. | `W2097716692` | Neutral condition provides baseline incentive contrast. | `psychopy_builtin` | `n/a` | Neutral branch preserves identical timing with zero-net outcome framing. |
