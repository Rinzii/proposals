SHELL := /usr/bin/env bash
.DEFAULT_GOAL := build
.NOTPARALLEL:

PAPER ?= 1219_homogeneous_parameters
PAPERS := $(sort $(notdir $(patsubst %/Makefile,%,$(wildcard papers/*/Makefile))))
PYTHON := md/wg21/deps/python/bin/python3
PORT ?= 8123

.PHONY: setup build build-all pdf pdf-all site assets serve watch update list-papers list-specs

setup:
	./scripts/setup.sh "$(PAPER)"

build: setup
	$(MAKE) -C "papers/$(PAPER)" html

build-all: setup
	@for paper in $(PAPERS); do $(MAKE) -C "papers/$$paper" html || exit; done

pdf: setup
	$(MAKE) -C "papers/$(PAPER)" pdf

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
	$(MAKE) -C "papers/$(PAPER)" serve html SERVE_PORT="$(PORT)"

update: setup
	$(MAKE) -C "papers/$(PAPER)" update

list-papers list-specs:
	@printf '%s\n' $(PAPERS)
