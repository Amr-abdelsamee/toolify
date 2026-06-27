"""
Hugging Face Hub utilities for Toolify.
"""

import os
from pathlib import Path
from typing import Optional, Sequence, Literal

try:
    from ..tools import pct
except ImportError:
    from toolify.tools import pct


__all__ = [
    "get_hf_dataset_size",
    "get_hf_model_size",
    "download_hf_repo",
    "download_hf_dataset",
    "download_hf_model",
]


RepoType = Literal["model", "dataset", "space"]


def _require_huggingface_hub():
    """Import huggingface_hub lazily so Toolify does not require it unless needed."""
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise ImportError(
            "This function requires 'huggingface-hub'. "
            "Install it with: pip install huggingface-hub"
        ) from exc

    return HfApi, snapshot_download


def _repo_id_to_dir_name(repo_id: str, use_full_name: bool = False) -> str:
    """Converts a Hugging Face repo ID into a safe local directory name."""
    if use_full_name:
        return repo_id.replace("/", "_")

    return repo_id.split("/")[-1]


def _bytes_to_gb(size_bytes: int) -> float:
    """Converts bytes to GB."""
    return size_bytes / (1024**3)


def _enable_hf_transfer(enable_hf_transfer: bool) -> None:
    """Enables hf_transfer for faster downloads if requested."""
    if enable_hf_transfer:
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"


def _get_safetensors_total_size(safetensors_meta) -> Optional[int]:
    """Safely extracts total safetensors size from metadata."""
    total_size = getattr(safetensors_meta, "total_size", None)

    if total_size is not None:
        return int(total_size)

    metadata = getattr(safetensors_meta, "metadata", None)
    if isinstance(metadata, dict) and metadata.get("total_size") is not None:
        return int(metadata["total_size"])

    files_metadata = getattr(safetensors_meta, "files_metadata", None)
    if isinstance(files_metadata, dict):
        total = 0

        for file_meta in files_metadata.values():
            size = getattr(file_meta, "size", None)
            if size is not None:
                total += int(size)

        if total > 0:
            return total

    return None


def _print_download_size(repo_id: str, size_gb: Optional[float]) -> None:
    """Prints a common download-size message."""
    pct(f"Will download: {repo_id}", "magenta")
    pct("=========================================", "cyan")

    if size_gb is not None:
        pct(f"Expected download size: ~{size_gb:.2f} GB", "cyan")
    else:
        pct("Expected download size: unknown", "yellow")

    pct("=========================================", "cyan")


def get_hf_dataset_size(
    repo_id: str,
    token: Optional[str | bool] = None,
    revision: Optional[str] = None,
    verbose: bool = True,
    raise_on_error: bool = False,
) -> Optional[float]:
    """Gets the Hugging Face reported dataset storage size in GB.

    Args:
        repo_id: Dataset repository ID, e.g. "MBZUAI/ClArTTS".
        token: Hugging Face token. Use True to use the locally saved token.
        revision: Optional branch, tag, or commit hash.
        verbose: If True, prints the result.
        raise_on_error: If True, raises exceptions instead of returning None.

    Returns:
        Dataset size in GB if available, otherwise None.
    """
    HfApi, _ = _require_huggingface_hub()

    try:
        api = HfApi(token=token)

        info = api.dataset_info(
            repo_id=repo_id,
            revision=revision,
            expand=["usedStorage"],
        )

        used_storage_bytes = getattr(info, "usedStorage", None)

        if used_storage_bytes is None:
            if verbose:
                pct(f"Storage size is not available for dataset: {repo_id}", "yellow")
            return None

        size_gb = _bytes_to_gb(int(used_storage_bytes))

        if verbose:
            pct(f"Hub-reported total storage: {size_gb:.2f} GB", "cyan")

        return round(size_gb, 2)

    except Exception as exc:
        if raise_on_error:
            raise

        if verbose:
            pct(f"Could not get dataset storage size for {repo_id}: {exc}", "red")

        return None


def get_hf_model_size(
    repo_id: str,
    token: Optional[str | bool] = None,
    revision: Optional[str] = None,
    prefer_safetensors: bool = True,
    verbose: bool = True,
    raise_on_error: bool = False,
) -> Optional[float]:
    """Gets the approximate Hugging Face model download size in GB.

    The function first tries safetensors metadata because it is usually accurate
    for model weight files. If unavailable, it falls back to summing file sizes
    from model repository metadata.

    Args:
        repo_id: Model repository ID, e.g. "Qwen/Qwen3-Embedding-0.6B".
        token: Hugging Face token. Use True to use the locally saved token.
        revision: Optional branch, tag, or commit hash.
        prefer_safetensors: If True, tries safetensors metadata first.
        verbose: If True, prints progress messages.
        raise_on_error: If True, raises exceptions instead of returning None.

    Returns:
        Approximate model size in GB if available, otherwise None.
    """
    HfApi, _ = _require_huggingface_hub()
    api = HfApi(token=token)

    try:
        total_bytes = 0

        if prefer_safetensors:
            try:
                safetensors_meta = api.get_safetensors_metadata(
                    repo_id=repo_id,
                    revision=revision,
                )

                total_bytes = _get_safetensors_total_size(safetensors_meta)

                if total_bytes is None:
                    raise ValueError("Could not extract total safetensors size.")

                if verbose:
                    pct("Used safetensors metadata for model weight size.", "green")

                return round(_bytes_to_gb(total_bytes), 2)

            except Exception:
                if verbose:
                    pct(
                        "No usable safetensors metadata found. Falling back to file metadata.",
                        "yellow",
                    )

        info = api.model_info(
            repo_id=repo_id,
            revision=revision,
            files_metadata=True,
        )

        total_bytes = 0
        for file in info.siblings:
            file_size = getattr(file, "size", None)
            if file_size is not None:
                total_bytes += int(file_size)

        if total_bytes == 0:
            if verbose:
                pct(f"Could not estimate model size for {repo_id}.", "red")
            return None

        return round(_bytes_to_gb(total_bytes), 2)

    except Exception as exc:
        if raise_on_error:
            raise

        if verbose:
            pct(f"Could not get model size for {repo_id}: {exc}", "red")

        return None


def download_hf_repo(
    repo_id: str,
    repo_type: RepoType = "model",
    base_dir: str | Path = ".",
    local_dir: Optional[str | Path] = None,
    token: Optional[str | bool] = None,
    revision: Optional[str] = None,
    allow_patterns: Optional[str | Sequence[str]] = None,
    ignore_patterns: Optional[str | Sequence[str]] = None,
    max_workers: int = 8,
    enable_hf_transfer: bool = False,
    use_full_repo_name: bool = False,
    verbose: bool = True,
    **snapshot_kwargs,
) -> Path:
    """Downloads a Hugging Face repository to a local directory.

    Args:
        repo_id: Hugging Face repo ID.
        repo_type: Repository type: "model", "dataset", or "space".
        base_dir: Base directory used when local_dir is not provided.
        local_dir: Exact local directory to download into. If provided, base_dir is ignored.
        token: Hugging Face token. Use True to use the locally saved token.
        revision: Optional branch, tag, or commit hash.
        allow_patterns: Optional file patterns to include.
        ignore_patterns: Optional file patterns to exclude.
        max_workers: Number of concurrent download workers.
        enable_hf_transfer: If True, sets HF_HUB_ENABLE_HF_TRANSFER=1.
        use_full_repo_name: If True, "org/name" becomes "org_name".
            If False, only "name" is used.
        verbose: If True, prints progress messages.
        **snapshot_kwargs: Extra keyword arguments passed to snapshot_download().

    Returns:
        Local path to the downloaded repository.
    """
    valid_repo_types = {"model", "dataset", "space"}
    if repo_type not in valid_repo_types:
        raise ValueError(
            f"repo_type must be one of {sorted(valid_repo_types)}, got {repo_type!r}"
        )

    _enable_hf_transfer(enable_hf_transfer)

    _, snapshot_download = _require_huggingface_hub()

    if local_dir is None:
        repo_dir_name = _repo_id_to_dir_name(
            repo_id,
            use_full_name=use_full_repo_name,
        )
        local_dir = Path(base_dir) / repo_dir_name
    else:
        local_dir = Path(local_dir)

    local_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        pct(f"Syncing {repo_type}: {repo_id} → {local_dir}", "yellow")

    downloaded_path = snapshot_download(
        repo_id=repo_id,
        repo_type=repo_type,
        local_dir=str(local_dir),
        token=token,
        revision=revision,
        allow_patterns=allow_patterns,
        ignore_patterns=ignore_patterns,
        max_workers=max_workers,
        **snapshot_kwargs,
    )

    downloaded_path = Path(downloaded_path)

    if verbose:
        pct(f"Done syncing → {downloaded_path}", "green")

    return downloaded_path


def download_hf_dataset(
    repo_id: str,
    base_dir: str | Path = "datasets",
    local_dir: Optional[str | Path] = None,
    token: Optional[str | bool] = None,
    revision: Optional[str] = None,
    allow_patterns: Optional[str | Sequence[str]] = None,
    ignore_patterns: Optional[str | Sequence[str]] = None,
    max_workers: int = 8,
    enable_hf_transfer: bool = False,
    show_size: bool = True,
    use_full_repo_name: bool = True,
    verbose: bool = True,
    **snapshot_kwargs,
) -> Path:
    """Downloads a Hugging Face dataset.

    Args:
        repo_id: Dataset repo ID.
        base_dir: Base directory used when local_dir is not provided.
        local_dir: Exact local directory to download into. If provided, base_dir is ignored.
        token: Hugging Face token. Use True to use the locally saved token.
        revision: Optional branch, tag, or commit hash.
        allow_patterns: Optional file patterns to include.
        ignore_patterns: Optional file patterns to exclude.
        max_workers: Number of concurrent download workers.
        enable_hf_transfer: If True, sets HF_HUB_ENABLE_HF_TRANSFER=1.
        show_size: If True, estimates and prints dataset size before download.
        use_full_repo_name: If True, "org/name" becomes "org_name".
            If False, only "name" is used.
        verbose: If True, prints progress messages.
        **snapshot_kwargs: Extra keyword arguments passed to snapshot_download().

    Returns:
        Local path to the downloaded dataset.
    """
    if show_size and verbose:
        size_gb = get_hf_dataset_size(
            repo_id=repo_id,
            token=token,
            revision=revision,
            verbose=verbose,
            raise_on_error=False,
        )
        _print_download_size(repo_id, size_gb)

    return download_hf_repo(
        repo_id=repo_id,
        repo_type="dataset",
        base_dir=base_dir,
        local_dir=local_dir,
        token=token,
        revision=revision,
        allow_patterns=allow_patterns,
        ignore_patterns=ignore_patterns,
        max_workers=max_workers,
        enable_hf_transfer=enable_hf_transfer,
        use_full_repo_name=use_full_repo_name,
        verbose=verbose,
        **snapshot_kwargs,
    )


def download_hf_model(
    repo_id: str,
    base_dir: str | Path = "models",
    local_dir: Optional[str | Path] = None,
    token: Optional[str | bool] = None,
    revision: Optional[str] = None,
    allow_patterns: Optional[str | Sequence[str]] = None,
    ignore_patterns: Optional[str | Sequence[str]] = None,
    max_workers: int = 16,
    enable_hf_transfer: bool = False,
    show_size: bool = True,
    use_full_repo_name: bool = False,
    verbose: bool = True,
    **snapshot_kwargs,
) -> Path:
    """Downloads a Hugging Face model.

    Args:
        repo_id: Model repo ID, e.g. "facebook/nllb-200-3.3B".
        base_dir: Base directory used when local_dir is not provided.
        local_dir: Exact local directory to download into. If provided, base_dir is ignored.
        token: Hugging Face token. Use True to use the locally saved token.
        revision: Optional branch, tag, or commit hash.
        allow_patterns: Optional file patterns to include.
        ignore_patterns: Optional file patterns to exclude.
        max_workers: Number of concurrent download workers.
        enable_hf_transfer: If True, sets HF_HUB_ENABLE_HF_TRANSFER=1.
        show_size: If True, estimates and prints model size before download.
        use_full_repo_name: If True, "org/name" becomes "org_name".
            If False, only "name" is used.
        verbose: If True, prints progress messages.
        **snapshot_kwargs: Extra keyword arguments passed to snapshot_download().

    Returns:
        Local path to the downloaded model.
    """
    if show_size and verbose:
        size_gb = get_hf_model_size(
            repo_id=repo_id,
            token=token,
            revision=revision,
            verbose=verbose,
            raise_on_error=False,
        )
        _print_download_size(repo_id, size_gb)

    return download_hf_repo(
        repo_id=repo_id,
        repo_type="model",
        base_dir=base_dir,
        local_dir=local_dir,
        token=token,
        revision=revision,
        allow_patterns=allow_patterns,
        ignore_patterns=ignore_patterns,
        max_workers=max_workers,
        enable_hf_transfer=enable_hf_transfer,
        use_full_repo_name=use_full_repo_name,
        verbose=verbose,
        **snapshot_kwargs,
    )
