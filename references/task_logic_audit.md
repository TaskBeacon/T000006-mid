# Task Logic Audit

## 1. Paradigm Intent

This task implements a Monetary Incentive Delay (MID) paradigm to probe incentive anticipation, rapid target responding, and outcome evaluation under win/lose/neutral cue conditions. A condition-specific adaptive controller tunes target duration to maintain target hit-rate pressure.

Primary evidence anchors:
- `W2119128116`: core MID state model (cue -> anticipation -> target -> feedback).
- `W2096412262`: feedback/outcome event separation relevance for EEG analysis.
- `W2097716692`: incentive-condition contrasts across repeated trial blocks.

## 2. Block/Trial Workflow

Block workflow:
1. Show instruction stage.
2. For each block, generate condition list from configured conditions.
3. Emit block onset trigger.
4. Run all trials with shared controller state.
5. Emit block end trigger.
6. Show block summary (hit rate and score).

Trial workflow:
1. `cue`: display `win/lose/neut` cue (`cue_duration`).
2. `anticipation_fixation`: fixation interval with early-response capture.
3. `target_response_window`: show condition-specific target for adaptive duration; capture response/timeout.
4. `prefeedback_fixation`: brief fixation interval.
5. `feedback`: condition- and hit/miss-specific text feedback.
6. Update adaptive controller using hit/miss outcome and condition.

## 3. Condition Semantics

| Condition | Cue Meaning | Hit Outcome | Miss Outcome |
|---|---|---|---|
| `win` | Potential reward trial | `+delta` | `0` |
| `lose` | Potential loss-avoidance trial | `0` | `-delta` |
| `neut` | Neutral control trial | `0` | `0` |

Additional rule:
- Early keypress during `anticipation_fixation` is treated as miss regardless of subsequent target response.

## 4. Response and Scoring Rules

- Valid response key set is `task.key_list` (current profiles use `space`).
- Target hit logic:
  - Hit: response within adaptive target duration and no early response in anticipation stage.
  - Miss: timeout in target stage or early anticipation response.
- Score update (`feedback_delta`):
  - `win`: `+delta` on hit, `0` on miss.
  - `lose`: `0` on hit, `-delta` on miss.
  - `neut`: `0` regardless of hit/miss.
- Controller update is called each trial with `(hit, condition)`.

## 5. Stimulus Layout Plan

- Screen units: `deg`.
- Centered single-object presentation per phase.
- Cue phase uses condition-specific geometric shapes with color-coded valence:
  - `win_cue`: magenta circle
  - `lose_cue`: yellow square
  - `neut_cue`: cyan triangle
- Target phase uses black geometric counterpart per condition.
- Feedback phase uses centered Chinese text (SimHei) for hit/miss outcome display.
- Block and instruction screens are centered multiline text/textbox layouts.

## 6. Trigger Plan

| Phase/Event | Trigger Key | Code |
|---|---|---:|
| Experiment start/end | `exp_onset` / `exp_end` | 98 / 99 |
| Block start/end | `block_onset` / `block_end` | 100 / 101 |
| Fixation onset | `fixation_onset` | 1 |
| Win cue/anticipation/target | `win_cue_onset` / `win_anti_onset` / `win_target_onset` | 10 / 11 / 12 |
| Win feedback hit/miss | `win_hit_fb_onset` / `win_miss_fb_onset` | 13 / 14 |
| Win key/timeout | `win_key_press` / `win_no_response` | 15 / 16 |
| Lose cue/anticipation/target | `lose_cue_onset` / `lose_anti_onset` / `lose_target_onset` | 20 / 21 / 22 |
| Lose feedback hit/miss | `lose_hit_fb_onset` / `lose_miss_fb_onset` | 23 / 24 |
| Lose key/timeout | `lose_key_press` / `lose_no_response` | 25 / 26 |
| Neutral cue/anticipation/target | `neut_cue_onset` / `neut_anti_onset` / `neut_target_onset` | 30 / 31 / 32 |
| Neutral feedback hit/miss | `neut_hit_fb_onset` / `neut_miss_fb_onset` | 33 / 34 |
| Neutral key/timeout | `neut_key_press` / `neut_no_response` | 35 / 36 |

## 7. Architecture Decisions (Auditability)

- `main.py` centralizes mode flow (`human|qa|sim`) and shared execution order.
- `src/run_trial.py` handles all trial state transitions with explicit phase labels.
- Participant-facing text is config-driven through `stimuli` entries.
- Adaptive timing lives in task-specific controller (`src/utils.py`) and is documented in config `controller` section.
- Sampler responder is phase-aware and aligned to task-specific phase labels (`anticipation_fixation`, `target_response_window`).

## 8. Inference Log

| Decision | Type | Rationale |
|---|---|---|
| Early anticipation response counted as miss | inferred | Prevents pre-target keypress from being scored as valid target hit in incentive-delay logic. |
| Specific cue/target colors and shapes retained | inferred | Preserves current task implementation while maintaining clear condition separability. |
| Controller target accuracy set to `0.66` | inferred | Keeps adaptive difficulty near canonical MID hit-rate operating range. |
