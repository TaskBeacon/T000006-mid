from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class _HitParams:
    win: float = 0.82
    neut: float = 0.70
    lose: float = 0.60
    default: float = 0.68


@dataclass
class _RtParams:
    win: float = 0.23
    neut: float = 0.27
    lose: float = 0.31
    default: float = 0.28
    sigma: float = 0.05
    min_rt: float = 0.12


class MidSamplerResponder:
    """Task-specific MID sampler responder.

    Behavior:
    - instruction/block/goodbye: always continue with a key press.
    - anticipation: mostly no response, with small early-press probability.
    - target: condition-dependent hit/miss + RT sampling.
    """

    def __init__(
        self,
        *,
        key: str = "space",
        p_early: float = 0.02,
        continue_rt_s: float = 0.25,
        p_hit_win: float = 0.82,
        p_hit_neut: float = 0.70,
        p_hit_lose: float = 0.60,
        p_hit_default: float = 0.68,
        rt_mu_win: float = 0.23,
        rt_mu_neut: float = 0.27,
        rt_mu_lose: float = 0.31,
        rt_mu_default: float = 0.28,
        rt_sigma: float = 0.05,
        rt_min_s: float = 0.12,
    ):
        self._rng: Any = None
        self._session: SessionInfo | None = None
        self.key = str(key)
        self.p_early = float(p_early)
        self.continue_rt_s = float(continue_rt_s)
        self.hit = _HitParams(
            win=float(p_hit_win),
            neut=float(p_hit_neut),
            lose=float(p_hit_lose),
            default=float(p_hit_default),
        )
        self.rt = _RtParams(
            win=float(rt_mu_win),
            neut=float(rt_mu_neut),
            lose=float(rt_mu_lose),
            default=float(rt_mu_default),
            sigma=float(rt_sigma),
            min_rt=float(rt_min_s),
        )

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._session = session
        self._rng = rng

    def _condition(self, obs: Observation) -> str:
        cond = (obs.condition_id or "").strip().lower()
        if cond:
            return cond
        raw = obs.task_factors.get("condition")
        return str(raw).strip().lower() if raw is not None else ""

    def _pick_key(self, valid_keys: list[str]) -> str | None:
        if not valid_keys:
            return None
        if self.key in valid_keys:
            return self.key
        return valid_keys[0]

    def _deadline(self, obs: Observation) -> float | None:
        if obs.deadline_s is not None:
            return float(obs.deadline_s)
        if obs.response_window_s is not None:
            return float(obs.response_window_s)
        return None

    def _min_wait(self, obs: Observation) -> float:
        raw = obs.extras.get("min_wait_s")
        try:
            return max(0.0, float(raw))
        except Exception:
            return 0.0

    def _clamp_or_miss(self, rt_s: float, deadline_s: float | None, min_wait_s: float) -> float | None:
        rt = max(float(rt_s), float(min_wait_s), float(self.rt.min_rt))
        if deadline_s is not None and rt > float(deadline_s):
            return None
        return rt

    def _draw_target_rt(self, cond: str) -> float:
        if cond == "win":
            mu = self.rt.win
        elif cond == "lose":
            mu = self.rt.lose
        elif cond == "neut":
            mu = self.rt.neut
        else:
            mu = self.rt.default
        return float(self._rng.gauss(mu, self.rt.sigma))

    def _p_hit(self, cond: str) -> float:
        if cond == "win":
            return self.hit.win
        if cond == "lose":
            return self.hit.lose
        if cond == "neut":
            return self.hit.neut
        return self.hit.default

    def act(self, obs: Observation) -> Action:
        if isinstance(obs, dict):
            obs = Observation.from_dict(obs)

        if self._rng is None:
            raise RuntimeError("MidSamplerResponder.start_session must be called before act().")

        valid_keys = list(obs.valid_keys or [])
        key = self._pick_key(valid_keys)
        if key is None:
            return Action(key=None, rt_s=None, meta={"source": "mid_sampler", "reason": "no_valid_key"})

        phase = (obs.phase or "").strip().lower()
        cond = self._condition(obs)
        deadline = self._deadline(obs)
        min_wait = self._min_wait(obs)

        # Continue screens should always advance.
        if phase in ("instruction_text", "block", "goodbye"):
            rt = self._clamp_or_miss(self.continue_rt_s, deadline, min_wait)
            if rt is None:
                return Action(key=None, rt_s=None, meta={"source": "mid_sampler", "phase": phase, "reason": "late"})
            return Action(key=key, rt_s=rt, meta={"source": "mid_sampler", "phase": phase})

        # Early presses in anticipation are rare.
        if phase == "anticipation":
            if self._rng.random() > self.p_early:
                return Action(
                    key=None,
                    rt_s=None,
                    meta={"source": "mid_sampler", "phase": phase, "condition": cond, "reason": "withhold"},
                )
            rt = self._clamp_or_miss(self.continue_rt_s, deadline, min_wait)
            if rt is None:
                return Action(
                    key=None,
                    rt_s=None,
                    meta={"source": "mid_sampler", "phase": phase, "condition": cond, "reason": "early_late"},
                )
            return Action(
                key=key,
                rt_s=rt,
                meta={"source": "mid_sampler", "phase": phase, "condition": cond, "reason": "early_press"},
            )

        # MID target: condition-dependent miss/hit + RT model.
        if phase == "target":
            p_hit = self._p_hit(cond)
            if self._rng.random() > p_hit:
                return Action(
                    key=None,
                    rt_s=None,
                    meta={"source": "mid_sampler", "phase": phase, "condition": cond, "reason": "miss", "p_hit": p_hit},
                )
            rt_raw = self._draw_target_rt(cond)
            rt = self._clamp_or_miss(rt_raw, deadline, min_wait)
            if rt is None:
                return Action(
                    key=None,
                    rt_s=None,
                    meta={
                        "source": "mid_sampler",
                        "phase": phase,
                        "condition": cond,
                        "reason": "late",
                        "rt_raw": rt_raw,
                        "p_hit": p_hit,
                    },
                )
            return Action(
                key=key,
                rt_s=rt,
                meta={
                    "source": "mid_sampler",
                    "phase": phase,
                    "condition": cond,
                    "p_hit": p_hit,
                    "rt_raw": rt_raw,
                },
            )

        return Action(key=None, rt_s=None, meta={"source": "mid_sampler", "phase": phase, "reason": "ignore_phase"})

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        return None
