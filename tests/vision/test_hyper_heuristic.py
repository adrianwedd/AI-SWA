import unittest
from pathlib import Path
import json

from core.task import Task
from vision import VisionEngine, RLHyperHeuristicAgent


class TestHyperHeuristicAgent(unittest.TestCase):
    def _task(self, id, ubv, tc, rr, size):
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

    def test_suggest_orders_by_wsjf(self):
        agent = RLHyperHeuristicAgent(exploration=0)
        t1 = self._task(1, 10, 2, 1, 5)  # 2.6
        t2 = self._task(2, 5, 1, 1, 2)   # 3.5
        t3 = self._task(3, 8, 0, 0, 4)   # 2.0
        ordered = agent.suggest([t1, t2, t3])
        self.assertEqual([t.id for t in ordered], [2, 1, 3])

    def test_shadow_mode_logs_history(self):
        log_file = Path("history.log")
        agent = RLHyperHeuristicAgent(history_path=log_file, exploration=0)
        ve = VisionEngine(rl_agent=agent, shadow_mode=True)
        t1 = self._task(1, 1, 1, 1, 1)
        t2 = self._task(2, 1, 1, 1, 2)
        ve.prioritize([t1, t2])
        self.assertEqual(len(agent.history), 1)
        self.assertTrue(log_file.exists())
        data = json.loads(log_file.read_text().strip())
        self.assertIn("baseline", data)
        log_file.unlink()

    def test_training_updates_weights(self):
        agent = RLHyperHeuristicAgent(exploration=0)
        metrics = {"gain": 0.5, "success": 1}
        start = agent.heuristic_weights["wsjf"]
        reward = agent.train(metrics)
        self.assertGreaterEqual(reward, 0.0)
        self.assertAlmostEqual(agent.heuristic_weights["wsjf"], start + 0.05)
        self.assertEqual(agent.training_data[0], metrics)

