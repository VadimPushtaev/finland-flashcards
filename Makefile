.PHONY: all combine

# Prefer Poetry if available; fall back to system python
PY := $(shell if command -v poetry >/dev/null 2>&1; then echo "poetry run python"; else echo "python"; fi)

all: combine

combine:
	$(PY) card_creator/combine_all_cards.py

