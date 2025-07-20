from reflector.rl.reward import calculate_reward, reward_terms, DEFAULT_WEIGHTS


def test_reward_terms_extraction():
    metrics = {
        "success": True,
        "runtime": 2.0,
        "style_score": 0.5,
        "complexity_score": 0.3,
        "doc_coverage": 0.8,
    }
    terms = reward_terms(metrics)
    assert terms["correctness"] == 1.0
    assert terms["performance"] == -2.0
    assert terms["style"] == 0.5
    assert terms["complexity"] == 0.3
    assert terms["doc_coverage"] == 0.8


def test_reward_terms_lint_score():
    metrics = {"success": True, "lint_score": 0.8}
    terms = reward_terms(metrics)
    assert terms["style"] == 0.8


def test_weighted_reward():
    metrics = {
        "success": 1,
        "runtime": 1,
        "style_score": 1,
        "complexity_score": 1,
        "doc_coverage": 1,
    }
    reward, _ = calculate_reward(
        metrics,
        weights={"correctness": 1, "performance": 1, "style": 1, "complexity": 1, "doc_coverage": 1},
    )
    assert reward == 1 - 1 + 1 + 1 + 1


def test_configured_weights(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """reward:\n  correctness: 2\n  performance: 0.1\n  style: 0\n  complexity: 0.5\n"""
    )
    monkeypatch.setenv("CONFIG_FILE", str(cfg))
    metrics = {
        "success": 1,
        "runtime": 2,
        "style_score": 1,
        "complexity_score": 4,
    }
    reward, _ = calculate_reward(metrics)
    assert reward == 2 * 1 + 0.1 * -2 + 0 + 0.5 * 4


def test_test_success_with_runtime():
    metrics = {"tests_passed": 9, "tests_failed": 1, "runtime": 2}
    reward, terms = calculate_reward(metrics, weights={"correctness": 1, "performance": 1})
    assert terms["correctness"] == 0.9
    assert terms["performance"] == -2
    assert reward == 0.9 - 2


def test_doc_coverage_term():
    metrics = {"doc_coverage": 0.6}
    terms = reward_terms(metrics)
    assert terms["doc_coverage"] == 0.6


def test_integration_pass_rate_reward():
    low = {"integration_pass_rate": 0.2}
    high = {"integration_pass_rate": 0.8}
    w = {"integration_pass_rate": 1}
    r_low, _ = calculate_reward(low, weights=w)
    r_high, _ = calculate_reward(high, weights=w)
    assert r_high > r_low
