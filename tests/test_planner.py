import pytest

from core.task import Task
from core import planner_utils


def create_task(task_factory, id, priority, status, dependencies=None, description="A task"):
    return task_factory(
        id=id,
        priority=priority,
        status=status,
        dependencies=dependencies or [],
        description=description,
    )


def test_empty_tasks_list(planner):
    """Planner should return ``None`` when given no tasks."""
    assert planner.plan([]) is None


def test_no_actionable_tasks_all_done(planner, task_factory):
    """Return ``None`` when every task has status ``done``."""
    task = create_task(task_factory, "t1", 10, "done")
    assert planner.plan([task]) is None


def test_no_actionable_tasks_all_inprogress(planner, task_factory):
    """Return ``None`` when all tasks are in progress."""
    task = create_task(task_factory, "t1", 10, "in_progress")
    assert planner.plan([task]) is None


def test_priority_selection(planner, task_factory):
    """Choose task with highest priority among pending ones."""
    task1 = create_task(task_factory, "t1", 10, "pending")
    task2 = create_task(task_factory, "t2", 20, "pending")
    task3 = create_task(task_factory, "t3", 5, "pending")
    selected = planner.plan([task1, task2, task3])
    assert selected.id == "t2"


def test_select_only_pending_tasks(planner, task_factory):
    """Ignore tasks not marked as ``pending``."""
    task1 = create_task(task_factory, "t1", 10, "done")
    task2 = create_task(task_factory, "t2", 20, "pending")
    task3 = create_task(task_factory, "t3", 5, "other_status")
    selected = planner.plan([task1, task2, task3])
    assert selected and selected.id == "t2"


def test_dependency_unmet_because_dependency_is_pending(planner, task_factory):
    """Blocked tasks should not be selected if dependency still pending."""
    dep = create_task(task_factory, "dep1", 5, "pending")
    main = create_task(task_factory, "main1", 10, "pending", ["dep1"])
    selected = planner.plan([dep, main])
    assert selected.id == "dep1"


def test_dependency_unmet_because_dependency_is_in_progress(planner, task_factory):
    """Select next unblocked task when dependency is in progress."""
    dep = create_task(task_factory, "dep1", 5, "in_progress")
    main = create_task(task_factory, "main1", 10, "pending", ["dep1"])
    other = create_task(task_factory, "other", 1, "pending")
    selected = planner.plan([dep, main, other])
    assert selected.id == "other"


def test_dependency_met(planner, task_factory):
    """Choose task once its dependency is done."""
    dep = create_task(task_factory, "dep1", 5, "done")
    main = create_task(task_factory, "main1", 10, "pending", ["dep1"])
    other = create_task(task_factory, "other", 1, "pending")
    selected = planner.plan([dep, main, other])
    assert selected.id == "main1"


def test_dependency_missing_in_list(planner, task_factory):
    """Skip task if dependency id is not found."""
    main = create_task(task_factory, "main1", 10, "pending", ["dep_missing"])
    other = create_task(task_factory, "other", 5, "pending")
    selected = planner.plan([main, other])
    assert selected.id == "other"


def test_complex_scenario_priority_and_dependencies(planner, task_factory):
    """Simulate a sequence of tasks becoming ready over time."""
    done = create_task(task_factory, "td1", 1, "done")
    blocked_missing = create_task(task_factory, "tpb_missing", 20, "pending", ["td_missing"])
    ready = create_task(task_factory, "tpd1", 10, "pending", ["td1"])
    low_prio = create_task(task_factory, "tpnlp", 5, "pending")
    blocked_pending = create_task(task_factory, "tpdp", 15, "pending", ["tpnlp"])

    tasks = [done, blocked_missing, ready, low_prio, blocked_pending]
    assert planner.plan(tasks).id == "tpd1"

    ready.status = "done"
    assert planner.plan(tasks).id == "tpnlp"

    low_prio.status = "done"
    assert planner.plan(tasks).id == "tpdp"

    blocked_pending.status = "done"
    assert planner.plan(tasks) is None


def test_no_actionable_all_blocked_by_unmet_dependency(planner, task_factory):
    """Return ``None`` when every pending task is blocked by another."""
    task_a = create_task(task_factory, "task_a", 10, "pending", ["task_b"])
    task_b = create_task(task_factory, "task_b", 5, "in_progress")
    assert planner.plan([task_a, task_b]) is None


def test_no_actionable_all_blocked_by_missing_dependency(planner, task_factory):
    """Return ``None`` when dependencies refer to missing tasks."""
    task_a = create_task(task_factory, "task_a", 10, "pending", ["task_missing"])
    assert planner.plan([task_a]) is None


def test_task_with_no_dependencies_attribute(planner, task_factory):
    """Tasks lacking ``dependencies`` attribute should still be runnable."""
    task_no_deps = create_task(task_factory, "t_no_dep_attr", 10, "pending")
    delattr(task_no_deps, "dependencies")
    selected = planner.plan([task_no_deps])
    assert selected and selected.id == "t_no_dep_attr"


def test_task_with_empty_dependencies_list(planner, task_factory):
    """Empty dependency list counts as all dependencies met."""
    task_empty_deps = create_task(task_factory, "t_empty_deps", 10, "pending", [])
    assert planner.plan([task_empty_deps]).id == "t_empty_deps"


def test_task_object_without_priority_attribute_defaults_to_zero(planner, task_factory):
    """Priority defaults to zero when attribute is absent."""
    task_no_prio = create_task(task_factory, "t_no_prio", 0, "pending", [])
    delattr(task_no_prio, "priority")
    task_prio = create_task(task_factory, "t_with_prio", 1, "pending")

    selected1 = planner.plan([task_no_prio, task_prio])
    assert selected1.id == "t_with_prio"

    selected2 = planner.plan([task_prio, task_no_prio])
    assert selected2.id == "t_with_prio"


def test_all_tasks_pending_no_dependencies_highest_priority_selected(planner, task_factory):
    """Select task with greatest priority when none are blocked."""
    tasks = [
        create_task(task_factory, "task_low", 1, "pending"),
        create_task(task_factory, "task_high", 10, "pending"),
        create_task(task_factory, "task_mid", 5, "pending"),
    ]
    assert planner.plan(tasks).id == "task_high"


def test_mix_of_statuses_dependencies_priority(planner, task_factory):
    """Ensure planner ignores non-pending and blocked tasks."""
    tasks = [
        create_task(task_factory, "done_dep", 1, "done"),
        create_task(task_factory, "pending_dep_on_done", 10, "pending", ["done_dep"]),
        create_task(task_factory, "pending_low_prio", 5, "pending"),
        create_task(task_factory, "in_progress_task", 100, "in_progress"),
        create_task(task_factory, "pending_blocked", 20, "pending", ["non_existent_dep"]),
    ]
    assert planner.plan(tasks).id == "pending_dep_on_done"


def test_duplicate_task_ids_raise_error(planner, task_factory):
    """Duplicate task IDs should raise an error."""
    tasks = [
        create_task(task_factory, "dup", 1, "pending"),
        create_task(task_factory, "dup", 2, "pending"),
    ]
    with pytest.raises(ValueError):
        planner.plan(tasks)


def test_warning_emitted_for_missing_dependency(planner, task_factory, caplog):
    """Emit warning when dependency id cannot be found."""
    task = create_task(task_factory, "main", 5, "pending", ["missing"])
    with caplog.at_level("WARNING"):
        planner.plan([task])
        assert any("missing" in m for m in caplog.text.splitlines())


def test_get_pending_tasks_helper(planner, task_factory):
    """Verify helper filters tasks by ``pending`` status."""
    tasks = [
        create_task(task_factory, "a", 1, "done"),
        create_task(task_factory, "b", 2, "pending"),
        create_task(task_factory, "c", 3, "in_progress"),
    ]
    pending = planner_utils.get_pending_tasks(tasks)
    assert len(pending) == 1 and pending[0].id == "b"


def test_dependencies_met_helper(planner, task_factory):
    """Check dependency evaluation logic."""
    dep_done = create_task(task_factory, "dep", 1, "done")
    main = create_task(task_factory, "main", 1, "pending", ["dep"])
    assert planner_utils.dependencies_met(main, [dep_done, main])

    dep_pending = create_task(task_factory, "dep_p", 1, "pending")
    blocked = create_task(task_factory, "blocked", 1, "pending", ["dep_p"])
    assert not planner_utils.dependencies_met(blocked, [blocked, dep_pending])

