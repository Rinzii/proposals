# Proposals

Bikeshed sources for C++ proposals by Ian Pike.

## Layout

```text
drafts/cpp/               Papers in progress
cpp/                      Papers that have a number and have been submitted
scripts/                  setup, build, and watch helpers
```


## Quick start

```sh
make setup
make update
make build
```

## Common commands

```sh
make build      # Build the default paper
make build-all  # Build everything in cpp/ and drafts/cpp/
make check      # Build the default paper and require nonempty output
make check-all  # Build every paper and require nonempty output
make list-specs # List paper sources
make watch      # Rebuild the selected paper on change
make update     # Update Bikeshed data files (needs network)
```

Build a single paper from either tree:

```sh
make build SPEC=drafts/cpp/P1219R3.bs
```

```sh
.venv/bin/bikeshed --no-update --die-on=warning --dry-run spec drafts/cpp/homogeneous_packs_r0.bs
```

See the [Bikeshed documentation](https://speced.github.io/bikeshed/) for
metadata, code blocks, references, and tables.
