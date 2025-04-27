# Monetary Incentive Delay (MID) Task – PsyFlow Version

This task implements a classical Monetary Incentive Delay (MID) paradigm, designed to measure reward anticipation and outcome processing under different motivational conditions. It is built using the [PsyFlow](https://taskbeacon.github.io/psyflow/) framework.



## Task Overview

Participants are instructed to respond as quickly and accurately as possible to a briefly presented target after a cue and anticipation phase. Each cue indicates the condition: potential reward ("win"), potential loss avoidance ("lose"), or neutral ("neut"). Feedback is given based on performance.

The task dynamically adjusts target duration to maintain a target hit rate (~66%) using an adaptive controller.



## Task Flow

| Step        | Description |
|-|-|
| Instruction | A textbox (`instruction_text`) presents task instructions in Chinese. Participants press **space bar** to begin. |
| Cue         | A visual shape (circle, square, or triangle) indicates the trial type (win, lose, neutral). |
| Anticipation | A fixation cross is displayed while participants prepare. |
| Target      | A brief target appears; participants must press the specified key (`down`) as quickly as possible. |
| Feedback    | Performance feedback is shown based on the hit/miss outcome. |
| ITI (Inter-Trial Interval) | A short blank screen is shown before the next trial. |
| Block Break | After each block, performance is summarized and participants rest. |
| Goodbye     | Final thank-you and score display. |



## Configuration Summary

All key settings are stored in the `config/config.yaml` file.

### Subject Info (`subinfo_fields`)
Participants are registered with:
- **Subject ID** (3-digit number from 101–999)
- **Session Name** (e.g., Practice, Experiment)
- **Experimenter Name**
- **Gender** (Male or Female)

Localizations for Chinese are defined via `subinfo_mapping`.



### Window Settings (`window`)
- Resolution: `1920 × 1080`
- Units: `deg`
- Fullscreen: `True`
- Monitor: `testMonitor`
- Background color: `gray`



### Stimuli (`stimuli`)
| Stimulus Name           | Type        | Description |
|-|-|-|
| `fixation`              | `text`      | Central fixation cross |
| `*_cue`                 | `circle/rect/polygon` | Visual cue for condition type (win/lose/neut) |
| `*_target`              | `circle/rect/polygon` | Target stimulus for response |
| `*_hit_feedback`        | `textbox`   | Feedback for hit trials |
| `*_miss_feedback`       | `textbox`   | Feedback for miss trials |
| `iti_stim`              | `text`      | Blank screen during ITI |
| `instruction_text`      | `textbox`   | Pre-task instruction screen |
| `instruction_image1/2`  | `image`     | Optional instructional images |
| `block_break`           | `textbox`   | Mid-task break and feedback screen |
| `good_bye`              | `textbox`   | End of task message and final score |



### Timing (`timing`)
| Phase          | Duration |
|-|-|
| Cue            | 0.3 seconds |
| Anticipation   | 1.0–1.2 seconds (randomized) |
| Target         | Adaptive (initial 0.3s, min 0.15s, max 0.5s) |
| Feedback       | 1 second |
| ITI            | 0.6–0.8 seconds (randomized) |



### Triggers (`triggers`)
The following event triggers are sent via `TriggerSender`:

| Event                | Codes |
|-|-|
| Win cue onset        | 10 |
| Lose cue onset       | 20 |
| Neut cue onset       | 30 |
| Anticipation onset   | 11, 21, 31 |
| Target onset         | 12, 22, 32 |
| Hit feedback onset   | 13, 23, 33 |
| Miss feedback onset  | 14, 24, 34 |
| Key press detected   | 15, 25, 35 |
| No response detected | 16, 26, 36 |
| Experiment start/end | 98 / 99 |
| Block start/end      | 100 / 101 |
| Fixation onset       | 1 |

Triggers can be customized for synchronization with EEG, fMRI, or other acquisition systems.



### Adaptive Controller (`controller`)
The MID task uses an adaptive staircase algorithm to maintain a target hit rate of **66%**.

| Parameter             | Value |
|-|-|
| Initial Target Duration | 0.3 seconds |
| Minimum Duration        | 0.15 seconds |
| Maximum Duration        | 0.5 seconds |
| Step Size               | 0.05 seconds |
| Target Accuracy         | 66% |
| Condition-Specific      | `True` (tracks separately for win, lose, neut) |

The controller updates target duration based on ongoing performance during each block.



## Running the Task


```python
python main.py
```