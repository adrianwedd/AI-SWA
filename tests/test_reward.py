from core.reward import calculate_reward


def test_reward_with_success_and_runtime():
    metrics = {"success": True, "runtime": 2.0}
    r = calculate_reward(metrics, success_weight=1.0, runtime_weight=0.5)
    assert r == 1.0 - 1.0


def test_reward_fallback_sum():
    metrics = {"coverage": 80, "bugs": 0}
    assert calculate_reward(metrics) == 80.0

