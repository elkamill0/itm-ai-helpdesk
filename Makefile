.ONESHELL:

format:
	poetry run ruff format .
	poetry run ruff check . --fix

check:
	poetry run ruff format --check .
	npx prettier client --check

test:
	poetry run pytest ./tests -vv
