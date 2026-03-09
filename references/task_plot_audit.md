# Task Plot Audit

- generated_at: 2026-03-10T00:17:26
- mode: existing
- task_path: E:\Taskbeacon\T000006-mid

## 1. Inputs and provenance

- E:\Taskbeacon\T000006-mid\README.md
- E:\Taskbeacon\T000006-mid\config\config.yaml
- E:\Taskbeacon\T000006-mid\src\run_trial.py

## 2. Evidence extracted from README

- | Step                | Description                                                                 |
- |---------------------|-----------------------------------------------------------------------------|
- | Cue                 | Show condition-specific cue (win/lose/neutral) with trigger                 |
- | Anticipation        | Display fixation; allow response (early keypress logged)                   |
- | Target              | Show target with adaptive duration; record response                        |
- | Pre-feedback Fixation | Display fixation before feedback                                          |
- | Feedback            | Present hit/miss feedback based on performance                             |
- | Adaptive Update     | Update target duration based on hit/miss outcome                           |

## 3. Evidence extracted from config/source

- win: phase=anticipation fixation, deadline_expr=settings.anticipation_duration, response_expr=settings.anticipation_duration, stim_expr='fixation'
- win: phase=target response window, deadline_expr=duration, response_expr=duration, stim_expr=f'{condition}_target'
- win: visible_show_without_context phase=feedback, unit_label_expr='feedback', duration_expr=settings.feedback_duration, stim_exprs=['fb_stim']
- lose: phase=anticipation fixation, deadline_expr=settings.anticipation_duration, response_expr=settings.anticipation_duration, stim_expr='fixation'
- lose: phase=target response window, deadline_expr=duration, response_expr=duration, stim_expr=f'{condition}_target'
- lose: visible_show_without_context phase=feedback, unit_label_expr='feedback', duration_expr=settings.feedback_duration, stim_exprs=['fb_stim']
- neut: phase=anticipation fixation, deadline_expr=settings.anticipation_duration, response_expr=settings.anticipation_duration, stim_expr='fixation'
- neut: phase=target response window, deadline_expr=duration, response_expr=duration, stim_expr=f'{condition}_target'
- neut: visible_show_without_context phase=feedback, unit_label_expr='feedback', duration_expr=settings.feedback_duration, stim_exprs=['fb_stim']

## 3b. Warnings

- win:feedback: participant-visible phase inferred from show() because set_trial_context(...) is missing
- lose:feedback: participant-visible phase inferred from show() because set_trial_context(...) is missing
- neut:feedback: participant-visible phase inferred from show() because set_trial_context(...) is missing

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 4
- screens_per_timeline: 6
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.037, right=0.039, blank=0.147
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0374, 'right_ratio': 0.0388, 'blank_ratio': 0.1471}
- validator_warnings:
  - timelines[0].phases[1] missing duration_ms; renderer will annotate as n/a.

## 7. Output files and checksums

- E:\Taskbeacon\T000006-mid\references\task_plot_spec.yaml: sha256=84daaa978104408ac98cfd5dbaa571463615281b5144fb9677c054c38612267b
- E:\Taskbeacon\T000006-mid\references\task_plot_spec.json: sha256=c0de39ed12feebc76d3824ade93133a8aa4e5bd6b3436c25793480a82b161323
- E:\Taskbeacon\T000006-mid\references\task_plot_source_excerpt.md: sha256=1f405d6d701a266f0fedb248406b27c8adbab6fe4b6b3ddcdfc496700455270f
- E:\Taskbeacon\T000006-mid\task_flow.png: sha256=af39ef323800d4a4e47ec921e32d61ce91f096c95b95e530d6e51cd91259ce89

## 8. Inferred/uncertain items

- win:target response window:unable to resolve duration from 'controller.get_duration(condition)'
- win:feedback:stimulus unresolved, used textual fallback
- lose:target response window:unable to resolve duration from 'controller.get_duration(condition)'
- lose:feedback:stimulus unresolved, used textual fallback
- neut:target response window:unable to resolve duration from 'controller.get_duration(condition)'
- neut:feedback:stimulus unresolved, used textual fallback
- collapsed equivalent condition logic into representative timeline: win, lose, neut
