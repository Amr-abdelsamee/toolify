import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import toolify.ai.huggingface as hf
from toolify.ai import (
    get_hf_model_size,
    get_hf_dataset_size,
    download_hf_model,
    download_hf_dataset,
)


GB = 1024**3


def test_ai_public_imports():
    assert callable(get_hf_model_size)
    assert callable(get_hf_dataset_size)
    assert callable(download_hf_model)
    assert callable(download_hf_dataset)


def test_get_hf_model_size_falls_back_when_safetensors_size_is_none(monkeypatch):
    """This test catches the real bug:
    safetensors metadata exists but total size cannot be extracted.
    The fallback must reset total_bytes to 0, not keep it as None.
    """

    class FakeHfApi:
        def __init__(self, token=None):
            self.token = token

        def get_safetensors_metadata(self, repo_id, revision=None):
            # No total_size, no metadata["total_size"], no files_metadata sizes.
            return SimpleNamespace()

        def model_info(self, repo_id, revision=None, files_metadata=True):
            return SimpleNamespace(
                siblings=[
                    SimpleNamespace(size=1 * GB),
                    SimpleNamespace(size=2 * GB),
                    SimpleNamespace(size=None),
                ]
            )

    monkeypatch.setattr(
        hf,
        "_require_huggingface_hub",
        lambda: (FakeHfApi, None),
    )

    size = hf.get_hf_model_size("org/test-model", verbose=False)

    assert size == 3.0


def test_get_hf_model_size_uses_safetensors_when_valid(monkeypatch):
    class FakeHfApi:
        def __init__(self, token=None):
            self.token = token

        def get_safetensors_metadata(self, repo_id, revision=None):
            return SimpleNamespace(total_size=4 * GB)

        def model_info(self, *args, **kwargs):
            raise AssertionError("model_info should not be called")

    monkeypatch.setattr(
        hf,
        "_require_huggingface_hub",
        lambda: (FakeHfApi, None),
    )

    size = hf.get_hf_model_size("org/test-model", verbose=False)

    assert size == 4.0


def test_get_hf_dataset_size(monkeypatch):
    class FakeHfApi:
        def __init__(self, token=None):
            self.token = token

        def dataset_info(self, repo_id, revision=None, expand=None):
            assert expand == ["usedStorage"]
            return SimpleNamespace(usedStorage=5 * GB)

    monkeypatch.setattr(
        hf,
        "_require_huggingface_hub",
        lambda: (FakeHfApi, None),
    )

    size = hf.get_hf_dataset_size("org/test-dataset", verbose=False)

    assert size == 5.0


def test_download_hf_model_uses_local_dir(monkeypatch, tmp_path):
    calls = {}

    class FakeHfApi:
        pass

    def fake_snapshot_download(**kwargs):
        calls.update(kwargs)

        local_dir = Path(kwargs["local_dir"])
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / "README.md").write_text("fake model", encoding="utf-8")

        return str(local_dir)

    monkeypatch.setattr(
        hf,
        "_require_huggingface_hub",
        lambda: (FakeHfApi, fake_snapshot_download),
    )

    target_dir = tmp_path / "custom_model"

    path = hf.download_hf_model(
        "org/test-model",
        local_dir=target_dir,
        show_size=False,
        verbose=False,
    )

    assert path == target_dir
    assert path.exists()
    assert (path / "README.md").exists()
    assert calls["repo_id"] == "org/test-model"
    assert calls["repo_type"] == "model"
    assert Path(calls["local_dir"]) == target_dir


def test_download_hf_dataset_uses_base_dir(monkeypatch, tmp_path):
    calls = {}

    class FakeHfApi:
        pass

    def fake_snapshot_download(**kwargs):
        calls.update(kwargs)

        local_dir = Path(kwargs["local_dir"])
        local_dir.mkdir(parents=True, exist_ok=True)
        (local_dir / "README.md").write_text("fake dataset", encoding="utf-8")

        return str(local_dir)

    monkeypatch.setattr(
        hf,
        "_require_huggingface_hub",
        lambda: (FakeHfApi, fake_snapshot_download),
    )

    path = hf.download_hf_dataset(
        "org/test-dataset",
        base_dir=tmp_path / "datasets",
        show_size=False,
        verbose=False,
    )

    expected = tmp_path / "datasets" / "org_test-dataset"

    assert path == expected
    assert path.exists()
    assert (path / "README.md").exists()
    assert calls["repo_id"] == "org/test-dataset"
    assert calls["repo_type"] == "dataset"
    assert Path(calls["local_dir"]) == expected


def test_download_hf_repo_rejects_invalid_repo_type(tmp_path):
    with pytest.raises(ValueError):
        hf.download_hf_repo(
            "org/test-repo",
            repo_type="invalid",  # type: ignore[arg-type]
            base_dir=tmp_path,
            verbose=False,
        )


@pytest.mark.integration
def test_integration_get_real_hf_model_size():
    """Real Hugging Face test.

    Run only when:
        RUN_HF_INTEGRATION=1 python -m pytest tests/test_ai.py -m integration -v
    """
    if os.getenv("RUN_HF_INTEGRATION") != "1":
        pytest.skip("Set RUN_HF_INTEGRATION=1 to run Hugging Face integration tests.")

    size = hf.get_hf_model_size(
        "Qwen/Qwen3-Reranker-0.6B",
        verbose=True,
        raise_on_error=True,
    )

    assert size is not None
    assert size > 0


@pytest.mark.integration
def test_integration_download_model_readme_only(tmp_path):
    """Downloads only tiny files from a real model repo."""
    if os.getenv("RUN_HF_INTEGRATION") != "1":
        pytest.skip("Set RUN_HF_INTEGRATION=1 to run Hugging Face integration tests.")

    path = hf.download_hf_model(
        "Qwen/Qwen3-Reranker-0.6B",
        local_dir=tmp_path / "qwen_reranker_test",
        allow_patterns=["README.md", "config.json"],
        show_size=False,
        verbose=True,
    )

    assert path.exists()
    assert any(path.iterdir())