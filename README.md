# Proposals

C and C++ proposals by Ian Pike. [Read the papers](https://rinzii.github.io/proposals/).

Run the local preview with `make serve`. To list or build individual papers, use

```sh
make list-papers
make build pdf PAPER=cxx/draft/variadic_comma
```

From a paper directory, `make` builds the HTML and prints its path. Use `make pdf` for the PDF.

Use fenced Markdown blocks for paper callouts. For example,

```markdown
::: decision
Should the conversion be explicit?
:::
```

The other block classes are `note`, `bug`, `draftnote`, and `ednote`. Use `::: {.draftnote audience="EWG"}` to name the audience. Inside `wording`, `note` uses the standard's note format and `add` marks inserted wording.

Use `::: {.recorded-poll label="Recorded EWG poll" result="Consensus."}` around a motion and vote table. Add `source="…"` to link the label to the record. Omit `result` when the record gives only counts. Use `::: {.proposed-poll label="Proposed EWG poll"}` around a proposed motion or numbered list. A block of removed wording uses `::: rm` inside `wording`.

Papers live in `papers/<language>/draft/<slug>/` or `papers/<language>/published/<slug>/`. Use `c` for C and `cxx` for C++. A unique slug such as `PAPER=variadic_comma` also works.

Only papers in `published/` appear in the hub. Share a draft at `drafts/<language>/<slug>/` under the site URL, replacing underscores in the slug with hyphens. Append `paper.pdf` for the PDF. Move the paper directory from `draft/` to `published/` to list it on the next site build. The share URL still works.
