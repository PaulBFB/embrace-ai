format:
	@echo "🖨️ Format code: Running ruff"
	@uvx ruff format

test:
	@echo "🔎 Testing code: Running pytest with coverage report HTMl"
	@uv run pytest --cov=src --cov-report=html --cov-report=term

#pack:
	@#echo "🗂️ Packaging code into flatfile - use as knowledge base for Claude/aider/etc."
	@#uvx repopack "$(CURDIR)" --ignore *lock*,.github/*,.mypy_cache/*,data/*,archive/*,architecture-diagram*,*.svg --output "codebase.txt"

mypy:
	@uv run mypy "$(CURDIR)"
