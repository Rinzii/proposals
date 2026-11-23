# Proposals

C and C++ proposals by Ian Pike. [Read the papers](https://rinzii.github.io/proposals/).

Run the local preview with `make serve`. To list or build individual papers, use

```sh
make list-papers
make build pdf PAPER=cxx/draft/variadic_comma
```

From a paper directory, `make` builds the HTML and prints its path. Use `make pdf` for the PDF.

Papers live in `papers/<language>/draft/<slug>/` or `papers/<language>/published/<slug>/`. Use `c` for C and `cxx` for C++. A unique slug such as `PAPER=variadic_comma` also works.

Only papers in `published/` appear in the hub. Share a draft at `drafts/<language>/<slug>/` under the site URL, replacing underscores in the slug with hyphens. Append `paper.pdf` for the PDF. Move the paper directory from `draft/` to `published/` to list it on the next site build. The share URL still works.
