.ONESHELL:

format:
	poetry run ruff format .
	poetry run ruff check . --fix

check:
	poetry run ruff format --check .

test:
	poetry run pytest ./tests -vv

install:
	poetry install
	poetry run pip uninstall -y $$(poetry run pip list --format=freeze | grep -E '^(torch|torchaudio|torchvision|nvidia-)' | cut -d '=' -f1) || echo "Brak pakietów do usunięcia"
	poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	poetry lock
