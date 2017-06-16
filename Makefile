GREP := $(shell command -v ggrep || command -v grep)
SED := $(shell command -v gsed || command -v sed)

help:
	@$(GREP) --only-matching --word-regexp '^[^[:space:].]*:' Makefile | SED 's|:[[:space:]]*||'

deps:
	mkdir -p deps
	cd deps && wget https://gist.githubusercontent.com/n8henrie/dc55b8fb366710003b5d3c557dfc4469/raw/4478029bf8213a0e8fef0cfd662a4a171c6e2aaf/whois.py

publish: deps
	rm -f index.zip 
	cd deps && zip --recurse-paths ../index.zip ../*.py *
	aws lambda update-function-code --function-name checkdomainexpiration --zip-file fileb://index.zip

clean-deps:
	rm -rf deps

.PHONY: help clean-deps
