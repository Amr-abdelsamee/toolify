# Releasing

Toolify follows `MAJOR.MINOR.PATCH` versioning:

- Increment `PATCH` for compatible bug fixes.
- Increment `MINOR` for backward-compatible features.
- Increment `MAJOR` for incompatible public API changes.

The package version belongs in `pyproject.toml`. Git tags use the same version
with a `v` prefix, such as `v1.0.0`.

## Release checklist

1. Choose the next version.
2. Update `version` in `pyproject.toml`.
3. Move changelog entries from `Unreleased` to the new version.
4. Run offline tests and build the documentation.
5. Build and inspect the wheel and source distribution.
6. Commit the release preparation.
7. Create and push the matching Git tag.
8. Publish a GitHub Release from that tag.
9. Confirm the GitHub workflow publishes the release to PyPI.

Validation commands:

```bash
python -m pytest -m "not integration"
mkdocs build --strict
python -m build
python -m twine check dist/*
```

Release tag example:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

PyPI releases are immutable. Never reuse a version that has already been
published.
