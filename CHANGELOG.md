# CHANGELOG

All notable development changes for `T000006-mid` are documented here.

## [1.1.1] - 2026-02-18

### Changed
- Refactored responder context phase names in `src/run_trial.py` to task-specific labels (removed generic MID-style phase naming).
- Updated stage comments in `src/run_trial.py` to phase-aligned labels for cleaner auditability.
- Updated `README.md` to keep runtime phase documentation aligned with the implemented trial context phases.

### Fixed
- Removed legacy stage comment patterns (`cue/anticipation/target/feedback`) from trial runtime code.

## [1.1.0] - 2026-02-16

### Added
- Added task-level multi-mode entry flow in `main.py` (`human`, `qa`, `sim`) with explicit CLI arguments and per-mode config defaults.
- Added simulation sampler responder at `responders/mid_sampler.py` (`MidSamplerResponder`) for MID-specific condition/phase-aware simulated responses.
- Added dedicated responder package exports in `responders/__init__.py`.
- Added simulation config profiles:
  - `config/config_scripted_sim.yaml` (default scripted sim profile)
  - `config/config_sampler_sim.yaml` (task-specific sampler sim profile)
- Added `config/config_qa.yaml` as the QA-focused runtime profile and embedded `qa.acceptance_criteria` for contract checks.
- Added TAPS contract adoption metadata in `taskbeacon.yaml`:
  - `contracts.psyflow_taps: v0.1.0`

### Changed
- Updated task runtime to use framework runtime context + responder seam for QA/sim while preserving human flow.
- Updated trial context injection to include standardized responder observation fields (trial/phase/deadline/valid keys/condition/block/task factors).
- Updated task trigger driver config to `triggers.driver.type` schema.
- Updated simulation responder config to `sim.responder.type` schema.
- Updated `.gitignore` to ignore `outputs/human/` artifact path.
- Updated task metadata in README:
  - Version: `main (1.1.0)`
  - Date Updated: `2026/02/16`
  - PsyFlow Version: `0.1.8`

### Fixed
- Removed mixed-mode sections from config profiles so each config only contains its own runtime scope (human/qa/scripted-sim/sampler-sim).

### TAPS Structure Notes
- Standardized task configs by role:
  - `config.yaml` for human runs
  - `config_qa.yaml` for QA/dev validation runs
  - `config_scripted_sim.yaml` and `config_sampler_sim.yaml` for simulation runs
- Simulation outputs are now mode-scoped under `outputs/` and can coexist with human output files without overwriting.

### QA/Sim Execution Summary
- `qa` mode: deterministic/runtime validation path for task logic, trigger events, and acceptance contract.
- `sim` mode: simulated responder path for generating behavioral traces with scripted or sampler responders.
