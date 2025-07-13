import pytest
from core.reflector import Reflector


def test_extract_refactor_filepath_variants():
    assert Reflector._extract_refactor_filepath("refactor a.py") == "a.py"
    assert Reflector._extract_refactor_filepath("update a.py") == "a.py"
    assert Reflector._extract_refactor_filepath("refactor module") is None
    assert Reflector._extract_refactor_filepath("refactor") is None


def test_check_required_fields_missing():
    refl = Reflector()
    tasks = [{"id": 1, "description": "hi"}]
    with pytest.raises(ValueError):
        refl._check_required_fields(tasks)


def test_calc_complexity_trend():
    assert Reflector._calc_complexity_trend([1, 2]) == "up"
    assert Reflector._calc_complexity_trend([3, 1]) == "down"
    assert Reflector._calc_complexity_trend([2, 2]) == "stable"
    assert Reflector._calc_complexity_trend([5]) == "stable"


def test_calc_rate():
    assert Reflector._calc_rate([1, 2, 4]) == pytest.approx(1.5)
    assert Reflector._calc_rate([1]) == "unknown"
    assert Reflector._calc_rate([]) == "unknown"


def test_is_duplicate_pending():
    existing = {"a.py": {"status": "pending"}}
    task = {"status": "pending"}
    assert Reflector._is_duplicate_pending("a.py", task, existing)
    task2 = {"status": "done"}
    assert not Reflector._is_duplicate_pending("a.py", task2, existing)
    assert not Reflector._is_duplicate_pending("b.py", task, existing)
