# Tests

This directory contains Toolify's offline and integration tests. Run commands
from the repository root.

## Running tests

### Run all offline tests

```bash
python -m pytest -m "not integration"
```

### Run a specific test file

```bash
python -m pytest tests/test_ai.py -v
```

### Run a specific test function

```bash
python -m pytest tests/test_ai.py::test_get_hf_model_size_uses_safetensors_when_valid -v
```

### Run integration tests

Integration tests require network access and are excluded by default:

```bash
RUN_HF_INTEGRATION=1 python -m pytest tests/test_ai.py -m integration -v
```

The `-v` option displays individual test names instead of only progress dots.
