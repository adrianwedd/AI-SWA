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


def test_configured_weights(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("""reward:\n  correctness: 2\n  performance: 0.1\n  style: 0\n""")
    monkeypatch.setenv("CONFIG_FILE", str(cfg))
    metrics = {"success": 1, "runtime": 2, "style_score": 1}
    reward, _ = calculate_reward(metrics)
    assert reward == 2 * 1 + 0.1 * -2 + 0


def test_test_success_with_runtime():
    metrics = {"tests_passed": 9, "tests_failed": 1, "runtime": 2}
    reward, terms = calculate_reward(metrics, weights={"correctness": 1, "performance": 1})
    assert terms["correctness"] == 0.9
    assert terms["performance"] == -2
    assert reward == 0.9 - 2
