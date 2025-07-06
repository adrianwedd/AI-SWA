"""Reflector coordinates strategic self-improvement decisions."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .self_auditor import SelfAuditor
from .observability import MetricsProvider
from .log_utils import configure_logging


class Reflector:
    """Run a reflection cycle to analyze and evolve the system."""

    def __init__(
        self,
        tasks_path: Path = Path("tasks.yml"),
        complexity_threshold: int = 15,
        analysis_paths: Optional[List[Path]] = None,
        metrics_provider: Optional["MetricsProvider"] = None,
    ) -> None:
        configure_logging()
        self.tasks_path = Path(tasks_path)
        self.complexity_threshold = complexity_threshold
        self.analysis_paths = analysis_paths or self._discover_analysis_paths()
        self.self_auditor = SelfAuditor(complexity_threshold=complexity_threshold)
        self.metrics_provider = metrics_provider
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    def run_cycle(self, tasks: Optional[List[Dict]] = None) -> List[Dict]:
        """Execute a full reflection cycle and persist any new tasks."""

        self.logger.info("Starting reflection cycle")

        if tasks is None:
            tasks = self._load_tasks()

        analysis_results = self.analyze()
        decisions = self.decide(analysis_results, tasks)
        new_tasks = self.execute(decisions, tasks)

        if new_tasks:
            updated_tasks = tasks + new_tasks
            self.validate(updated_tasks)
            self._save_tasks(updated_tasks)
            self.logger.info("Reflection cycle completed: %d new tasks", len(new_tasks))
        else:
            self.logger.info("Reflection cycle completed: no new tasks generated")

        return tasks + new_tasks

    # ------------------------------------------------------------------
    def analyze(self) -> Dict:
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "code_metrics": {},
            "system_health": {},
            "evolution_trends": {},
            "strategic_insights": [],
        }

        try:
            code_metrics = self.self_auditor.analyze(self.analysis_paths)
            analysis["code_metrics"] = self._summarize_code_metrics(code_metrics)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Code analysis failed: %s", exc)
            analysis["code_metrics"] = {"error": str(exc)}

        analysis["system_health"] = self._analyze_system_health()
        analysis["evolution_trends"] = self._analyze_evolution_trends()
        analysis["strategic_insights"] = self._generate_strategic_insights(analysis)

        if self.metrics_provider:
            analysis["observability_metrics"] = self.metrics_provider.collect()

        return analysis

    # ------------------------------------------------------------------
    def decide(self, analysis_results: Dict, current_tasks: List[Dict]) -> Dict:
        decisions = {
            "refactor_tasks": [],
            "architectural_improvements": [],
            "technical_debt_priorities": [],
            "new_capabilities": [],
            "process_improvements": [],
        }

        task_analysis = self._analyze_task_backlog(current_tasks)

        code_metrics = analysis_results.get("code_metrics", {})
        if code_metrics.get("needs_attention"):
            refactor_decisions = self._decide_refactoring_priorities(code_metrics, current_tasks)
            decisions["refactor_tasks"].extend(refactor_decisions)

        system_health = analysis_results.get("system_health", {})
        if system_health.get("architectural_issues"):
            arch = self._decide_architectural_improvements(system_health, current_tasks)
            decisions["architectural_improvements"].extend(arch)

        debt_decisions = self._decide_technical_debt_priorities(analysis_results, task_analysis)
        decisions["technical_debt_priorities"].extend(debt_decisions)

        capability_decisions = self._decide_new_capabilities(analysis_results, current_tasks)
        decisions["new_capabilities"].extend(capability_decisions)

        process_decisions = self._decide_process_improvements(task_analysis, analysis_results)
        decisions["process_improvements"].extend(process_decisions)

        self.logger.info("Strategic decisions made: %d categories", len(decisions))
        return decisions

    # ------------------------------------------------------------------
    def execute(self, decisions: Dict, current_tasks: List[Dict]) -> List[Dict]:
        new_tasks: List[Dict] = []
        next_id = max([task.get("id", 0) for task in current_tasks], default=0) + 1

        for ref in decisions["refactor_tasks"]:
            new_tasks.append(self._create_refactor_task(ref, next_id))
            next_id += 1
        for arch in decisions["architectural_improvements"]:
            new_tasks.append(self._create_architectural_task(arch, next_id))
            next_id += 1
        for debt in decisions["technical_debt_priorities"]:
            new_tasks.append(self._create_debt_task(debt, next_id))
            next_id += 1
        for cap in decisions["new_capabilities"]:
            new_tasks.append(self._create_capability_task(cap, next_id))
            next_id += 1
        for proc in decisions["process_improvements"]:
            new_tasks.append(self._create_process_task(proc, next_id))
            next_id += 1

        return new_tasks

    # ------------------------------------------------------------------
    def validate(self, tasks: List[Dict]) -> bool:
        task_ids = [task.get("id") for task in tasks if "id" in task]
        if len(task_ids) != len(set(task_ids)):
            dup = [i for i in task_ids if task_ids.count(i) > 1]
            raise ValueError(f"Duplicate task IDs found: {dup}")

        refactor_tasks = [t for t in tasks if "refactor" in t.get("description", "").lower()]
        refactor_files: Dict[str, Dict] = {}
        for task in refactor_tasks:
            desc = task.get("description", "")
            parts = desc.split()
            if len(parts) >= 2 and parts[1].endswith(".py"):
                filepath = parts[1]
                if filepath in refactor_files and task.get("status") == refactor_files[filepath].get("status") == "pending":
                    self.logger.warning(
                        "Potential duplicate refactor task for %s: tasks %s and %s",
                        filepath,
                        task.get("id"),
                        refactor_files[filepath].get("id"),
                    )
                else:
                    refactor_files[filepath] = task

        required = ["id", "description", "component", "dependencies", "priority", "status"]
        for task in tasks:
            missing = [f for f in required if f not in task]
            if missing:
                raise ValueError(f"Task {task.get('id', 'unknown')} missing fields: {missing}")

        return True

    # ------------------------------------------------------------------
    def _discover_analysis_paths(self) -> List[Path]:
        paths = []
        for pattern in ["core/*.py", "tests/*.py", "*.py"]:
            paths.extend(Path(".").glob(pattern))
        return [p for p in paths if p.is_file()]

    # ------------------------------------------------------------------
    def _load_tasks(self) -> List[Dict]:
        try:
            with open(self.tasks_path, "r") as f:
                return yaml.safe_load(f) or []
        except FileNotFoundError:
            self.logger.warning("Tasks file %s not found", self.tasks_path)
            return []
        except yaml.YAMLError as exc:
            self.logger.error("Failed to parse tasks file: %s", exc)
            return []

    # ------------------------------------------------------------------
    def _save_tasks(self, tasks: List[Dict]) -> None:
        with open(self.tasks_path, "w") as f:
            yaml.dump(tasks, f, default_flow_style=False, sort_keys=False)

    # ------------------------------------------------------------------
    def _summarize_code_metrics(self, metrics: Dict) -> Dict:
        summary = {
            "total_files": len(metrics),
            "files_needing_refactor": 0,
            "max_complexity": 0,
            "avg_complexity": 0,
            "complexity_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "needs_attention": False,
        }

        complexities: List[int] = []
        for data in metrics.values():
            if data.get("needs_refactor"):
                summary["files_needing_refactor"] += 1

            max_c = data.get("max_complexity", 0)
            complexities.append(max_c)
            summary["max_complexity"] = max(summary["max_complexity"], max_c)

            if max_c > 25:
                summary["complexity_distribution"]["critical"] += 1
            elif max_c > 15:
                summary["complexity_distribution"]["high"] += 1
            elif max_c > 10:
                summary["complexity_distribution"]["medium"] += 1
            else:
                summary["complexity_distribution"]["low"] += 1

        if complexities:
            summary["avg_complexity"] = sum(complexities) / len(complexities)

        summary["needs_attention"] = (
            summary["files_needing_refactor"] > 0 or summary["max_complexity"] > self.complexity_threshold
        )

        return summary

    # ------------------------------------------------------------------
    def _analyze_system_health(self) -> Dict:
        return {
            "architectural_issues": [],
            "test_coverage": "unknown",
            "dependency_health": "unknown",
            "documentation_coverage": "unknown",
        }

    # ------------------------------------------------------------------
    def _analyze_evolution_trends(self) -> Dict:
        return {
            "complexity_trend": "stable",
            "task_completion_rate": "unknown",
            "feature_velocity": "unknown",
        }

    # ------------------------------------------------------------------
    def _generate_strategic_insights(self, analysis: Dict) -> List[str]:
        insights: List[str] = []
        code = analysis.get("code_metrics", {})
        if code.get("files_needing_refactor", 0) > 3:
            insights.append(
                "High number of files need refactoring - consider dedicated refactoring sprint"
            )

        if code.get("max_complexity", 0) > 30:
            insights.append("Critical complexity detected - immediate attention required")

        return insights

    # ------------------------------------------------------------------
    def _analyze_task_backlog(self, tasks: List[Dict]) -> Dict:
        analysis = {
            "total_tasks": len(tasks),
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "done_tasks": 0,
            "duplicate_tasks": [],
            "priority_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }

        descriptions: Dict[str, int] = {}
        for task in tasks:
            status = task.get("status", "unknown")
            if status == "pending":
                analysis["pending_tasks"] += 1
            elif status == "in_progress":
                analysis["in_progress_tasks"] += 1
            elif status == "done":
                analysis["done_tasks"] += 1

            priority = task.get("priority", 3)
            if priority in analysis["priority_distribution"]:
                analysis["priority_distribution"][priority] += 1

            desc = task.get("description", "")
            if desc in descriptions:
                analysis["duplicate_tasks"].append({"description": desc, "task_ids": [descriptions[desc], task.get("id")]})
            else:
                descriptions[desc] = task.get("id")

        return analysis

    # ------------------------------------------------------------------
    def _decide_refactoring_priorities(self, code_metrics: Dict, current_tasks: List[Dict]) -> List[Dict]:
        decisions: List[Dict] = []
        if not code_metrics.get("needs_attention"):
            return decisions

        pending_refactors = [
            t
            for t in current_tasks
            if t.get("status") == "pending" and "refactor" in t.get("description", "").lower()
        ]

        if len(pending_refactors) > 5:
            decisions.append(
                {
                    "type": "refactor_consolidation",
                    "reason": "Too many pending refactor tasks",
                    "action": "consolidate_refactor_tasks",
                }
            )

        return decisions

    # ------------------------------------------------------------------
    def _decide_architectural_improvements(self, system_health: Dict, current_tasks: List[Dict]) -> List[Dict]:
        return []

    # ------------------------------------------------------------------
    def _decide_technical_debt_priorities(self, analysis: Dict, task_analysis: Dict) -> List[Dict]:
        decisions: List[Dict] = []
        if task_analysis.get("duplicate_tasks"):
            decisions.append(
                {
                    "type": "task_cleanup",
                    "reason": "Duplicate tasks detected",
                    "duplicates": task_analysis["duplicate_tasks"],
                }
            )
        return decisions

    # ------------------------------------------------------------------
    def _decide_new_capabilities(self, analysis: Dict, current_tasks: List[Dict]) -> List[Dict]:
        return []

    # ------------------------------------------------------------------
    def _decide_process_improvements(self, task_analysis: Dict, analysis: Dict) -> List[Dict]:
        decisions: List[Dict] = []
        if task_analysis.get("pending_tasks", 0) > 20:
            decisions.append(
                {
                    "type": "process_improvement",
                    "reason": "Large task backlog",
                    "suggestion": "task_prioritization_review",
                }
            )
        return decisions

    # ------------------------------------------------------------------
    def _create_refactor_task(self, decision: Dict, task_id: int) -> Dict:
        return {
            "id": task_id,
            "description": f"Refactor task consolidation - {decision['reason']}",
            "component": "refactor",
            "dependencies": [],
            "priority": 3,
            "status": "pending",
            "metadata": {"type": "refactor", "generated_by": "Reflector", "decision_type": decision["type"]},
        }

    # ------------------------------------------------------------------
    def _create_architectural_task(self, decision: Dict, task_id: int) -> Dict:
        return {
            "id": task_id,
            "description": f"Architectural improvement - {decision['reason']}",
            "component": "architecture",
            "dependencies": [],
            "priority": 4,
            "status": "pending",
            "metadata": {"type": "architecture", "generated_by": "Reflector", "decision_type": decision["type"]},
        }

    # ------------------------------------------------------------------
    def _create_debt_task(self, decision: Dict, task_id: int) -> Dict:
        description = f"Technical debt - {decision['reason']}"
        if decision["type"] == "task_cleanup":
            dup_count = len(decision.get("duplicates", []))
            description = f"Clean up {dup_count} duplicate tasks"

        return {
            "id": task_id,
            "description": description,
            "component": "maintenance",
            "dependencies": [],
            "priority": 2,
            "status": "pending",
            "metadata": {
                "type": "technical_debt",
                "generated_by": "Reflector",
                "decision_type": decision["type"],
                "details": decision,
            },
        }

    # ------------------------------------------------------------------
    def _create_capability_task(self, decision: Dict, task_id: int) -> Dict:
        return {
            "id": task_id,
            "description": f"New capability - {decision['reason']}",
            "component": "feature",
            "dependencies": [],
            "priority": 3,
            "status": "pending",
            "metadata": {"type": "capability", "generated_by": "Reflector", "decision_type": decision["type"]},
        }

    # ------------------------------------------------------------------
    def _create_process_task(self, decision: Dict, task_id: int) -> Dict:
        return {
            "id": task_id,
            "description": f"Process improvement - {decision['reason']}",
            "component": "process",
            "dependencies": [],
            "priority": 2,
            "status": "pending",
            "metadata": {"type": "process", "generated_by": "Reflector", "decision_type": decision["type"]},
        }


