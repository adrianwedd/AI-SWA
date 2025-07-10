from reflector.rl.reward import calculate_reward, reward_terms, DEFAULT_WEIGHTS


def test_reward_terms_extraction():
    metrics = {"success": True, "runtime": 2.0, "style_score": 0.5}
    terms = reward_terms(metrics)
    assert terms["correctness"] == 1.0
    assert terms["performance"] == -2.0
    assert terms["style"] == 0.5


def test_weighted_reward():
    metrics = {"success": 1, "runtime": 1, "style_score": 1}
    reward, _ = calculate_reward(metrics, weights={"correctness": 1, "performance": 1, "style": 1})
    assert reward == 1 - 1 + 1
