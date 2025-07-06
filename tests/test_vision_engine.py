import unittest
import json
import tempfile
from pathlib import Path

from core.task import Task
from vision.vision_engine import VisionEngine, RLAgent


class TestVisionEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

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

    def test_wsjf_sorting(self):
        t1 = self._task(1, 10, 2, 1, 5)  # score 2.6
        t2 = self._task(2, 5, 1, 1, 2)   # score 3.5
        t3 = self._task(3, 8, 0, 0, 4)   # score 2.0
        ve = VisionEngine()
        ordered = ve.prioritize([t1, t2, t3])
        self.assertEqual([t.id for t in ordered], [2, 1, 3])

    def test_rl_shadow_mode_records_history(self):
        agent = RLAgent()
        ve = VisionEngine(rl_agent=agent, shadow_mode=True)
        t1 = self._task(1, 1, 1, 1, 1)
        t2 = self._task(2, 1, 1, 1, 2)
        ve.prioritize([t1, t2])
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["baseline"], [1, 2])

    def test_rl_shadow_mode_logs_to_file(self):
        log_file = Path(self.tmpdir) / "history.log"
        agent = RLAgent(history_path=log_file)
        ve = VisionEngine(rl_agent=agent, shadow_mode=True)
        t1 = self._task(1, 1, 1, 1, 1)
        ve.prioritize([t1])
        self.assertTrue(log_file.exists())
        data = json.loads(log_file.read_text().strip())
        self.assertEqual(data["baseline"], [1])

    def test_rl_authority_applies_partial_order(self):
        class DummyAgent(RLAgent):
            def suggest(self, tasks):
                return list(reversed(tasks))

        agent = DummyAgent()
        ve = VisionEngine(rl_agent=agent, shadow_mode=False)
        agent.authority = 0.5
        t1 = self._task(1, 4, 2, 1, 1)
        t2 = self._task(2, 2, 1, 0, 1)
        t3 = self._task(3, 1, 0, 0, 1)
        ordered = ve.prioritize([t1, t2, t3])
        self.assertEqual([t.id for t in ordered], [3, 1, 2])

    def test_wsjf_handles_missing_metrics(self):
        """Tasks missing WSJF metrics should default to zero/one."""
        t1 = Task(
            id=1,
            description="",
            component="vision",
            dependencies=[],
            priority=1,
            status="pending",
        )
        t2 = self._task(2, 1, 1, 1, 2)
        ve = VisionEngine()
        ordered = ve.prioritize([t1, t2])
        self.assertEqual([t.id for t in ordered], [2, 1])

    def test_wsjf_zero_and_negative_job_size(self):
        """Zero job size defaults to one and negative values rank lowest."""
        t_zero = self._task(1, 4, 2, 1, 0)  # treated as size 1 => high score
        t_neg = self._task(2, 5, 0, 0, -2)  # negative size => negative score
        ve = VisionEngine()
        ordered = ve.prioritize([t_neg, t_zero])
        self.assertEqual([t.id for t in ordered], [1, 2])

    def test_rl_authority_full_ordering(self):
        """Authority of 1 should fully apply RL suggestions."""

        class ReverseAgent(RLAgent):
            def suggest(self, tasks):
                return list(reversed(tasks))

        agent = ReverseAgent()
        agent.authority = 1.0
        ve = VisionEngine(rl_agent=agent, shadow_mode=False)
        t1 = self._task(1, 1, 1, 1, 1)
        t2 = self._task(2, 1, 1, 1, 1)
        ordered = ve.prioritize([t1, t2])
        self.assertEqual([t.id for t in ordered], [2, 1])

    def test_rl_update_authority(self):
        """update_authority increases authority only on sufficient gain."""
        agent = RLAgent()
        agent.update_authority(0.1)
        self.assertAlmostEqual(agent.authority, 0.1)
        agent.update_authority(0.01)
        self.assertAlmostEqual(agent.authority, 0.1)
        agent.update_authority(0.95)
        self.assertLessEqual(agent.authority, 1.0)

