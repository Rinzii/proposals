SHELL := /usr/bin/env bash
.DEFAULT_GOAL := build

SPEC_DIRS := cpp drafts/cpp
OUT_DIR := out
DEFAULT_SPEC := drafts/cpp/annotation_customization.bs
SPEC ?= $(DEFAULT_SPEC)
OUT ?= $(OUT_DIR)/$(SPEC:.bs=.html)
SPECS := $(sort $(foreach dir,$(SPEC_DIRS),$(wildcard $(dir)/*.bs)))
OUTS := $(patsubst %.bs,$(OUT_DIR)/%.html,$(SPECS))

.PHONY: build build-all check check-all clean list-specs setup update watch

setup:
	./scripts/setup.sh

build:
	./scripts/build.sh "$(SPEC)" "$(OUT)"

build-all:
	./scripts/build.sh --all

check: build
	@test -s $(OUT)

check-all: build-all
	@for output in $(OUTS); do test -s "$$output"; done

list-specs:
	@printf '%s\n' $(SPECS)

update:
	if [[ -x .venv/bin/bikeshed ]]; then .venv/bin/bikeshed update; else bikeshed update; fi

watch:
	./scripts/watch.sh "$(SPEC)"

clean:
	rm -rf $(OUT_DIR)
