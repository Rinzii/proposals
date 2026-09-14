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
make build SPEC=drafts/cpp/annotation_customization.bs
make build SPEC=cpp/P1234.bs
```

Output mirrors the source path, so `drafts/cpp/foo.bs` renders to
`out/drafts/cpp/foo.html` and `cpp/foo.bs` to `out/cpp/foo.html`. A paper keeps
its own render when it graduates from one tree to the other.

## Publishing

CI renders any paper touched by a push to `main` and commits the result to the
`gh-pages` branch, preserving the `cpp/` and `drafts/cpp/` split. It renders
only changed files, so a push that touches neither tree produces no output.

## Optional dev container

Open the folder in VS Code and choose **Reopen in Container**. The container
installs Bikeshed automatically.
