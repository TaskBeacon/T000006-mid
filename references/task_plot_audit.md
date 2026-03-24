# Task Plot 审计

- generated_at: 2026-03-23T23:09:00
- mode: existing
- task_path: E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid

## 1. 输入与来源

- `README.md`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\README.md`
- `config.yaml`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\config\config.yaml`
- `run_trial.py`: `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\src\run_trial.py`

## 2. 从 README 提取的证据

- `README.md` 的 `Task Flow` 段同时包含块级流程和试次级流程。
- `Block-Level Flow` 只用于说明初始化、循环、保存数据等高层步骤。
- `Trial-Level Flow` 明确列出 `Cue`、`Anticipation`、`Target`、`Pre-feedback Fixation`、`Feedback`、`Adaptive Update`。

## 3. 从 config/source 提取的证据

- `Cue`：`make_unit(unit_label="cue").add_stim(stim_bank.get(f"{condition}_cue")).show(...)`。这是可见阶段，但源码没有 `set_trial_context(...)`，因此在审计中按 `show()` 推断。
- `Anticipation`：`set_trial_context(anti, ...)` 之后调用 `anti.capture_response(keys=settings.key_list, duration=settings.anticipation_duration)`；对应 1000–1200 ms 的注视/等待阶段。
- `Target`：`duration = controller.get_duration(condition)`，随后 `set_trial_context(target, ...)` 和 `target.capture_response(..., duration=duration)`；属于自适应目标窗，最终图中按 40–370 ms 展示。
- `Pre-Feedback`：`make_unit(unit_label="prefeedback_fixation").add_stim(stim_bank.get("fixation")).show(...)`，没有 `set_trial_context(...)`，本次按独立过渡阶段恢复。
- `Feedback`：`make_unit(unit_label="feedback").add_stim(fb_stim).show(...)`，同样没有 `set_trial_context(...)`；反馈刺激由 `condition` 与 `hit_type` 动态决定。

## 3b. 需要显式记录的警告

- `cue`：participant-visible phase inferred from `show()` because `set_trial_context(...)` is missing.
- `pre-feedback fixation`：participant-visible phase inferred from `show()` because `set_trial_context(...)` is missing.
- `feedback`：participant-visible phase inferred from `show()` because `set_trial_context(...)` is missing.

## 4. 映射到 task_plot_spec

- `root_key`: `task_plot_spec`
- `spec_version`: `0.2`
- 采用“一条条件一条时间线”的集合式图形。
- 选定条件为 `win`、`lose`、`neut`，每条时间线都保留 5 个阶段：`Cue`、`Anticipation`、`Target`、`Pre-Feedback`、`Feedback`。
- `Cue` 与 `Pre-Feedback` 是根据 `show()` 调用手工恢复的可见阶段，不再沿用旧图里的缺失结果。

## 5. 样式决策与理由

- 继续使用 timeline collection，因为这是 task-plot 的固定图型。
- 该任务的条件分支稳定且清晰，适合按条件分别绘制三条时间线。
- 每条时间线固定 5 个屏幕，能完整表达 MID 的 `Cue -> Anticipation -> Target -> Pre-Feedback -> Feedback` 顺序。

## 6. 渲染参数与约束

- `output_file`: `task_flow.png`
- `dpi`: `300`
- `max_conditions`: `3`
- `screens_per_timeline`: `5`
- `screen_overlap_ratio`: `0.1`
- `screen_slope`: `0.08`
- `screen_slope_deg`: `25.0`
- `screen_aspect_ratio`: `1.4545454545454546`
- `left_margin`: `0.2`
- `right_margin`: `0.03`
- `top_margin`: `0.03`
- `bottom_margin`: `0.05`
- `auto_width`: `false`
- `width_in`: `16.0`
- `qa_mode`: `local`
- `auto_layout_feedback`:
  - `layout pass 1: crop-only; left=0.058, right=0.067, blank=0.169`
- `auto_layout_feedback_records`:
  - `pass: 1`
    `metrics`: `{'left_ratio': 0.058, 'right_ratio': 0.067, 'blank_ratio': 0.169}`
- `validator_warnings`: 无

## 7. 输出文件与校验和

- `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\references\task_plot_spec.yaml`: `sha256=f48509faf7c27a65b00e2159c212af7b95a87cae8b02d6d62f7148e26ad2de4f`
- `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\references\task_plot_spec.json`: `sha256=f1b1d56257c37cb24c65331a94680f99525565c8df7e0d428a04c25b76372889`
- `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\references\task_plot_source_excerpt.md`: `sha256=fe6e83f30111c5b2fd79323651565bbd43bc077813b44236c6096c0a594f149b`
- `E:\xhmhc\TaskBeacon\benchmark\runs\task_plot_redo\T000006-mid\task_flow.png`: `sha256=e5e5125842fb303daeeaf24622e413d33e1d7ec60d77fb1170ce6c989fbab02b`

## 8. 推断项与不确定项

- `Target` 的最终时长来自自适应控制器，源码层面无法静态还原成单个固定值，因此图中用 40–370 ms 范围表达。
- `Cue`、`Pre-Feedback`、`Feedback` 都是从 `show()` 调用中恢复出的 participant-visible phase，不是 `set_trial_context(...)` 直接给出的上下文阶段。
- `Feedback` 仍然依赖 `condition` 与 `hit_type` 的组合，因此只适合用条件化示意，而不适合收敛成单一固定刺激。
