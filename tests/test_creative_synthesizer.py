from core.creative_synthesizer import CreativeSynthesizer


def test_generate_module(tmp_path):
    synth = CreativeSynthesizer()
    path = synth.generate("sample", directory=tmp_path)
    assert path.exists()
    text = path.read_text()
    assert "def main" in text

