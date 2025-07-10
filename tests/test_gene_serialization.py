from vision.epo import Gene


def test_gene_json_roundtrip(tmp_path):
    gene = Gene(architecture=(32, 16), learning_rate=0.002, clip_epsilon=0.1, gamma=0.95)
    path = tmp_path / "gene.json"
    gene.to_json(path)
    loaded = Gene.from_json(path)
    assert gene == loaded


def test_gene_mutation_ranges():
    gene = Gene()
    mutated = gene.mutate()
    assert all(1 <= l <= 256 for l in mutated.architecture)
    assert mutated.learning_rate >= 1e-5
    assert 0.01 <= mutated.clip_epsilon <= 1.0
    assert 0.5 <= mutated.gamma <= 0.999

