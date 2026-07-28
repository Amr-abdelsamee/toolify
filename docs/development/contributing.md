# Contributing

## Set up the project

```bash
git clone https://github.com/Amr-abdelsamee/toolify.git
cd toolify
pip install -e ".[dev,docs]"
```

## Make a change

1. Create a focused branch.
2. Keep public functions documented and exported through `__all__`.
3. Add or update tests for behavior changes.
4. Update the relevant guide and changelog entry.

Run validation before opening a pull request:

```bash
python -m pytest -m "not integration"
mkdocs build --strict
```

Use commit messages in the form:

```text
<type>(<scope>): <message>
```

Example:

```text
feat(audio): add waveform plotting
```
