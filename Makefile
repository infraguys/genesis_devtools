SHELL := bash
REPOSITORY := https://repository.genesis-core.tech
ifeq ($(SSH_KEY),)
	SSH_KEY = ~/.ssh/id_rsa.pub
endif

all: help

help:
	@echo "build_core       - build genesis core"
	@echo "bootstrap        - bootstrap genesis core"

mdlint:
	markdownlint-cli2 --config .markdownlint.yaml "**/*.md" "#node_modules" --fix

build_empty:
	genesis build -i $(SSH_KEY) -f ../genesis_empty -o ../genesis_empty/output --inventory --manifest-var repository=$(REPOSITORY)
