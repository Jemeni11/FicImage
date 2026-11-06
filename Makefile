# All commands use `uv run`

.PHONY: help dev lint format typecheck check clean publish

# Default target
help:
	@echo "FicImage dev tasks:"
	@echo ""
	@echo "  make dev        Install the package in editable mode"
	@echo "  make lint       Lint with ruff"
	@echo "  make format     Format code with ruff"
	@echo "  make typecheck  Type-check with ty"
	@echo "  make check      Run lint + typecheck (CI pipeline)"
	@echo "  make all        Run format + lint + typecheck + test"
	@echo "  make clean      Remove build artifacts and caches"
	@echo "  make publish    Push to PyPI"

# ── Dev ─────────────────────────────────────────────────────────────

dev:
	uv tool install --editable .

# ── Lint & Format ─────────────────────────────────────────────────────

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

format-check:
	uv run ruff format --check src/

# ── Type Check ────────────────────────────────────────────────────────

typecheck:
	uv run ty check src/

# ── Combined ──────────────────────────────────────────────────────────

check: lint typecheck
	@echo "✓ Lint and type checks passed"

all: format lint typecheck
	@echo "✓ All checks passed"

# ── Cleanup ───────────────────────────────────────────────────────────

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Clean"

# ── Publish ───────────────────────────────────────────────────────────

publish: clean
	uvx build
	uvx twine check dist/* && uvx twine upload dist/*
