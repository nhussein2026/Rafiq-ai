# Releasing

Rafiq uses [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.

- **PATCH** (0.1.1): bug fixes, new safety phrases, docs.
- **MINOR** (0.2.0): new features or skills, new approved source records.
- **MAJOR** (1.0.0): breaking changes to skills, schemas or the response format. 1.0.0 is reserved for a reviewed, production-ready release.

The version lives in **one place**: `__version__` in `src/rafiq/__init__.py`. `pyproject.toml` and the app UI read it from there.

## Steps

1. Move the items under `## [Unreleased]` in `CHANGELOG.md` to a new `## [X.Y.Z] - YYYY-MM-DD` section and update the compare links at the bottom.
2. Set `__version__ = "X.Y.Z"` in `src/rafiq/__init__.py`.
3. Commit: `git commit -am "chore: release vX.Y.Z"`.
4. Tag and push:
   ```bash
   git tag -a vX.Y.Z -m "Rafiq vX.Y.Z"
   git push origin main --tags
   ```
5. The **Release** workflow checks that the tag matches `__version__` and publishes a GitHub Release with the changelog notes.
