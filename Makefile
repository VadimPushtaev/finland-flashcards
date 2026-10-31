.PHONY: all combine combine-homebrew check-homebrew init-submodules kahoot

# Prefer Poetry if available; fall back to system python
PY := $(shell if command -v poetry >/dev/null 2>&1; then echo "poetry run python"; else echo "python"; fi)
KAHOOT_ARGS ?=

all: combine kahoot

init-submodules:
	git submodule update --init --recursive

combine:
	$(PY) card_creator/combine_all_cards.py
	$(PY) card_creator/homebrew/combine_chapters.py

combine-homebrew:
	$(PY) card_creator/homebrew/combine_chapters.py

check-homebrew:
	$(PY) card_creator/homebrew/combine_chapters.py --check

kahoot: init-submodules
	$(PY) card_creator/kahoot/export.py $(KAHOOT_ARGS)
