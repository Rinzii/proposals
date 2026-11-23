.DEFAULT_GOAL := all
DEFAULT_FORMAT ?= html
md_dir := $(dir $(lastword $(MAKEFILE_LIST)))
DEFAULTS := $(md_dir)defaults.yaml
PREFILTERS := $(md_dir)paper-style.py
PAPER_STYLES := $(wildcard $(md_dir)papers*.css) $(addprefix $(md_dir),paper-style.yaml paper-style.py wording-links.py papers.tex)
OUTDIR := $(md_dir)../out/papers/$(subst $(abspath $(md_dir)../papers)/,,$(CURDIR))

paper_id := $(word 1,$(subst :, ,$(PAPER_RULE)))
paper_src := $(word 2,$(subst :, ,$(PAPER_RULE)))
targets := $(addprefix $(paper_id).,html pdf latex)

.PHONY: all html pdf latex setup
all: $(DEFAULT_FORMAT)
html pdf latex: %: $(paper_id).%
	@printf '%s\n' "$(abspath $(OUTDIR)/$<)"

include $(md_dir)wg21/base.mk

override WATCHDEPS += $(PAPER_STYLES)

$(addprefix $(OUTDIR)/,$(targets)): $(paper_src).md $(DEPS) $(PAPER_STYLES) Makefile $(md_dir)mpark-wg21.mk | $(OUTDIR)
	$(PANDOC)

setup: $(GENDEPS)
