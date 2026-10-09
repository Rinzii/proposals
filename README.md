# Proposals

Bikeshed sources for C++ proposals by Ian Pike.

## Layout

```text
drafts/cpp/               Papers in progress
cpp/                      Papers that have a number and have been submitted
out/                      Local build output, mirrors the source tree
scratch/                  Local scratch space
scripts/                  setup, build, and watch helpers
```

`out/` and `scratch/` are gitignored. A paper starts in `drafts/cpp/` and moves
to `cpp/` once it has a P number.

## Quick start

```sh
./scripts/setup.sh
source .venv/bin/activate
make build
```

## Common commands

```sh
make build      # Build the default paper
make build-all  # Build everything in cpp/ and drafts/cpp/
make check      # Build and fail if output is empty
make list-specs # List paper sources
make watch      # Rebuild on change (needs watchexec or entr)
make clean      # Remove generated output
make update     # Update Bikeshed data files (needs network)
```

Build a single paper from either tree:

```sh
make build SPEC=drafts/cpp/invoking_annotations_r0.bs
make build SPEC=cpp/P1234.bs
```
