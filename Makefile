SHELL := /usr/bin/env bash
.DEFAULT_GOAL := build
.NOTPARALLEL:

PAPER ?= cxx/published/1219_homogeneous_parameters
PAPERS := $(patsubst papers/%/Makefile,%,$(sort $(wildcard papers/*/draft/*/Makefile papers/*/published/*/Makefile)))
paper_matches := $(filter $(PAPER) %/$(PAPER),$(PAPERS))
paper_dir = $(if $(filter 1,$(words $(paper_matches))),papers/$(paper_matches),$(error Select one paper with PAPER= from 'make list-papers' (requested '$(PAPER)')))
PYTHON := md/wg21/deps/python/bin/python3
PORT ?= 8123

.PHONY: setup paper-deps build build-all pdf pdf-all site assets serve watch update list-papers list-specs

setup:
	./scripts/setup.sh

paper-deps:
	$(MAKE) -C "$(paper_dir)" setup

build: setup
	$(MAKE) -C "$(paper_dir)" html

build-all: setup
	@for paper in $(PAPERS); do $(MAKE) -C "papers/$$paper" html || exit; done

pdf: setup
	$(MAKE) -C "$(paper_dir)" pdf

pdf-all: setup
	@for paper in $(PAPERS); do $(MAKE) -C "papers/$$paper" pdf || exit; done

assets: node_modules/typescript/bin/tsc
	npm run build

node_modules/typescript/bin/tsc: package.json package-lock.json
	npm ci

site: build-all pdf-all assets
	$(PYTHON) scripts/site.py --output out/site $(addprefix papers/,$(PAPERS))

serve: site
	$(PYTHON) scripts/serve.py --port "$(PORT)"

watch: setup
	$(MAKE) -C "$(paper_dir)" serve html SERVE_PORT="$(PORT)"

update: setup
	$(MAKE) -C "$(paper_dir)" update

list-papers list-specs:
	@printf '%s\n' $(PAPERS)
