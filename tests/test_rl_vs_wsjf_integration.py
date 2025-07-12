from pathlib import Path

from core.task import Task
from vision.vision_engine import VisionEngine, RLAgent
from vision.wsjf import wsjf_score


def _task(id, ubv, tc, rr, size):
    t = Task(
        id=id,
        description="",
        component="vision",
        dependencies=[],
        priority=1,
        status="pending",
    )
    t.user_business_value = ubv
    t.time_criticality = tc
    t.risk_reduction = rr
    t.job_size = size
    return t


def test_rl_vs_wsjf(tmp_path):
    tasks = [_task(1, 10, 2, 1, 5), _task(2, 5, 1, 1, 2), _task(3, 8, 0, 0, 4)]
    baseline_engine = VisionEngine()
    baseline_order = baseline_engine.prioritize(list(tasks))
    baseline_ids = [t.id for t in baseline_order]

    class ReverseAgent(RLAgent):
        def suggest(self, tasks):
            return list(reversed(tasks))

    agent = ReverseAgent(history_path=tmp_path / "history.log")
    agent.authority = 1.0
    rl_engine = VisionEngine(rl_agent=agent, shadow_mode=False)
    rl_order = rl_engine.prioritize(list(tasks))
    rl_ids = [t.id for t in rl_order]

    assert baseline_ids != rl_ids

    baseline_scores = [wsjf_score(t) for t in baseline_order]
    rl_scores = [wsjf_score(t) for t in rl_order]
    assert rl_scores != baseline_scores
