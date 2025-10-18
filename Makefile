.PHONY: deps
deps:
	mkdir -p deps
	pushd deps && curl --silent -LO https://gist.githubusercontent.com/n8henrie/dc55b8fb366710003b5d3c557dfc4469/raw/4478029bf8213a0e8fef0cfd662a4a171c6e2aaf/whois.py

.PHONY: publish
publish: deps
	rm -f index.zip 
	cd deps && zip --recurse-paths ../index.zip ../*.py *
	aws lambda update-function-code --function-name checkdomainexpiration --zip-file fileb://index.zip

.PHONY: clean-deps
clean-deps:
	rm -rf deps .venv

.venv: deps
	python3 -m venv .venv
	.venv/bin/python -m pip install boto3
	find .venv/lib -type d -name site-packages -exec cp ./deps/whois.py {} \; -quit
	
.PHONY: test
test: .venv
	./.venv/bin/python -m unittest ./test_checkdomainexpiration.py
