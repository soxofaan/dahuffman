

# Unreleased: 0.4.2

- Switch to GitHub Actions for CI (instead of Travis CI)
- Various documentation and readme tweaks
- Add type annotations ([#12](https://github.com/soxofaan/dahuffman/issues/12), [#13](https://github.com/soxofaan/dahuffman/pull/13), by [@KOLANICH](https://github.com/KOLANICH))
- Introduce code formatting tools; black, isort, pre-commit
- Eliminate `pkg_resources` dependency and switch to `importlib.resources` for Python 3.12+ compatibility ([#19](https://github.com/soxofaan/dahuffman/issues/19))
- Switch to `pyproject.toml` based project metadata ([#21](https://github.com/soxofaan/dahuffman/issues/21))


# 0.4.1 (2020-06-10)

- Fix packaging of `dahuffman.codecs` ([#10](https://github.com/soxofaan/dahuffman/issues/10))
