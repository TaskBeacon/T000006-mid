# 源码摘录（Monetary Incentive Delay (MID) Task）

## 输入文件
- `README.md`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\README.md`
- `config.yaml`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\config\config.yaml`
- `run_trial.py`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\src\run_trial.py`

## 选定条件
- `win`
- `lose`
- `neut`

## 关键试次流程证据
- `Cue`：`make_unit(unit_label="cue").add_stim(stim_bank.get(f"{condition}_cue")).show(...)`，条件提示直接由 `show()` 呈现，没有 `set_trial_context(...)`。
- `Anticipation`：`set_trial_context(anti, ...)` 后调用 `anti.capture_response(keys=settings.key_list, duration=settings.anticipation_duration)`，对应 1000–1200 ms 的注视/等待阶段。
- `Target`：`duration = controller.get_duration(condition)`，随后 `set_trial_context(target, ...)` 和 `target.capture_response(..., duration=duration)`；这是自适应目标窗，范围约 40–370 ms。
- `Pre-Feedback`：`make_unit(unit_label="prefeedback_fixation").add_stim(stim_bank.get("fixation")).show(...)`，没有 `set_trial_context(...)`，本次按独立过渡阶段恢复。
- `Feedback`：`make_unit(unit_label="feedback").add_stim(fb_stim).show(...)`，同样没有 `set_trial_context(...)`，反馈刺激由 `condition` 与 `hit_type` 动态决定。

## 备注
- `README.md` 中的 `Task Flow` 主要提供块级流程；试次级流程以 `run_trial.py` 为准。
- 本次从零重绘时，`Cue` 和 `Pre-Feedback` 两个阶段都是根据源码里的 `show()` 调用重新补回，而不是沿用旧图中的结果。
