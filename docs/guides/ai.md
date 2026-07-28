# Hugging Face

The AI module provides repository size inspection and snapshot downloads.

## Inspect sizes

```python
from toolify.ai import get_hf_dataset_size, get_hf_model_size

model_size_gb = get_hf_model_size("organization/model-name")
dataset_size_gb = get_hf_dataset_size("organization/dataset-name")
```

The functions return a size in GB when metadata is available, otherwise
`None`. Use `verbose=False` to suppress output or `raise_on_error=True` to
propagate API errors.

## Download a model or dataset

```python
from toolify.ai import download_hf_dataset, download_hf_model

model_path = download_hf_model(
    "organization/model-name",
    base_dir="models",
)

dataset_path = download_hf_dataset(
    "organization/dataset-name",
    base_dir="datasets",
)
```

Use `allow_patterns` or `ignore_patterns` to control which repository files
are downloaded:

```python
from toolify.ai import download_hf_model

path = download_hf_model(
    "organization/model-name",
    local_dir="models/example",
    allow_patterns=["README.md", "config.json"],
    show_size=False,
)
```

`download_hf_repo` is the shared lower-level helper for models, datasets, and
Spaces. Private repositories can use a token or the locally saved Hugging Face
credentials.
