.DEFAULT_GOAL := all
DEFAULT_FORMAT ?= html
DEFAULTS := ../../md/defaults.yaml
PREFILTERS := ../../md/paper-style.py
PAPER_STYLES := $(wildcard ../../md/papers*.css) ../../md/paper-style.yaml ../../md/paper-style.py ../../md/papers.tex
OUTDIR := ../../out/papers/$(notdir $(CURDIR))

paper_id := $(word 1,$(subst :, ,$(PAPER_RULE)))
paper_src := $(word 2,$(subst :, ,$(PAPER_RULE)))
targets := $(addprefix $(paper_id).,html pdf latex)

.PHONY: all html pdf latex setup
all: $(DEFAULT_FORMAT)
html: $(paper_id).html
pdf: $(paper_id).pdf
latex: $(paper_id).latex

include ../../md/wg21/base.mk

override WATCHDEPS += $(PAPER_STYLES)

$(addprefix $(OUTDIR)/,$(targets)): $(paper_src).md $(DEPS) $(PAPER_STYLES) | $(OUTDIR)
	$(PANDOC)

setup: $(GENDEPS)
