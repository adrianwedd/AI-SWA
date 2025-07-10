from reflector.rl.evolution import HyperParams


def test_hyperparams_json_roundtrip(tmp_path):
    params = HyperParams(
        buffer_capacity=4,
        actor_lr=0.001,
        critic_lr=0.002,
        gamma=0.95,
        clip_epsilon=0.3,
        sample_strategy="fifo",
    )
    path = tmp_path / "params.json"
    params.to_json(path)
    loaded = HyperParams.from_json(path)
    assert params == loaded


def test_hyperparams_mutation_ranges():
    params = HyperParams()
    mutated = params.mutate()
    assert mutated.buffer_capacity >= 2
    assert mutated.actor_lr >= 1e-5
    assert mutated.critic_lr >= 1e-5
    assert 0.5 <= mutated.gamma <= 0.999
    assert 0.05 <= mutated.clip_epsilon <= 1.0
    assert mutated.sample_strategy == params.sample_strategy
