from reflector import feature_vector


def test_feature_vector_from_metrics(tmp_path):
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"b": 2, "a": 1, "text": "ignore"}')
    vec = feature_vector(metrics_file)
    assert vec == [1.0, 2.0]
