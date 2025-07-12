"""Weighted Shortest Job First (WSJF) calculator."""

from core.task import Task


def wsjf_score(task: Task) -> float:
    """Return the WSJF score for ``task``.

    The score is computed as (user_business_value + time_criticality +
    risk_reduction) / job_size. Missing metrics default to zero and a
    job size of zero is treated as one.
    """
    cod = (
        getattr(task, "user_business_value", 0)
        + getattr(task, "time_criticality", 0)
        + getattr(task, "risk_reduction", 0)
    )
    job_size = getattr(task, "job_size", 1)
    if job_size == 0:
        job_size = 1
    return cod / job_size
