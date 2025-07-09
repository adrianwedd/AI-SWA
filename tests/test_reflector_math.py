from core.reflector import Reflector


def test_calc_rate_and_trend():
    assert Reflector._calc_rate([1, 3, 6]) == 2.5
    assert Reflector._calc_rate([1]) == "unknown"
    assert Reflector._calc_complexity_trend([1, 5]) == "up"
    assert Reflector._calc_complexity_trend([5, 1]) == "down"
    assert Reflector._calc_complexity_trend([5, 5]) == "stable"
