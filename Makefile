.PHONY: regen test

regen:
	python scripts/regen_examples.py

test:
	pytest
