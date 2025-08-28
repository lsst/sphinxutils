.PHONY: help
help:
	@echo "Make targets:"
	@echo "make init - Set up dev environment and install pre-commit hooks"
	@echo "make clean - Remove generated files"

.PHONY: clean
clean:
	rm -rf .tox
	rm -rf doc/_build

.PHONY: init
init:
	pip install -U uv
	uv pip install tox tox-uv
	uv pip install -e ".[dev]"
	pre-commit install
	rm -rf .tox
