from core.rl.reward import (
    calculate_reward,
    complexity_penalty,
    linting_bonus,
    integration_stability,
)


def test_complexity_penalty():
    simple = {"a.py": "def func():\n    return 1\n"}
    complex_code = {
        "b.py": (
            "def func(x):\n"
            "    for i in range(x):\n"
            "        if i % 2 == 0:\n"
            "            x += i\n"
            "    return x\n"
        )
    }
    p_simple = complexity_penalty(simple)
    p_complex = complexity_penalty(complex_code)
    assert p_complex < p_simple


def test_linting_bonus():
    good = {
        "good.py": (
            '"""module"""\n\n'
            "def good_func():\n"
            '    """doc"""\n'
            "    return 1\n"
        )
    }
    bad = {"bad.py": "def bad(x):\n    return x\n"}
    b_good = linting_bonus(good)
    b_bad = linting_bonus(bad)
    assert b_good > b_bad


def test_integration_stability():
    low = {"integration_pass_rate": 0.2}
    high = {"integration_pass_rate": 0.9}
    assert integration_stability(high) > integration_stability(low)


def test_calculate_reward_aggregation():
    changeset = {
        "good.py": (
            '"""m"""\n\n'
            "def good_func():\n"
            '    """doc"""\n'
            "    return 1\n"
        )
    }
    tests = {"integration_pass_rate": 0.8}
    reward = calculate_reward(changeset, tests)
    assert reward > 0
