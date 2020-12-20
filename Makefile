PROJ_SLUG = luna
CLI_NAME = luna
PY_VERSION = 3.8
LINTER = flake8
FORMATTER = black

freeze:
	pip freeze > requirements.txt

lint:
	$(LINTER) $(PROJ_SLUG)

format:
	$(FORMATTER) $(PROJ_SLUG)

test:
	py.test -s --cov-report term --cov=$(PROJ_SLUG) tests/

check: format lint test

coverage:
	py.test --cov-report html --cov=$(PROJ_SLUG) tests/

clean:
	rm -rf dist \
	rm -rf docs/build \
	rm -rf *.egg-info
	coverage erase

run_api:
	uvicorn luna.api.api:app --reload --host 0.0.0.0 --port 8000

run_api_prod:
	uvicorn luna.api.api:app --host 0.0.0.0 --port 8000
