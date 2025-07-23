# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for exploring AI/LLM coding practices. The codebase uses modern Python tooling with a simple structure focused on learning and experimentation.

## Development Commands

### Testing
- `make test` - Run pytest with coverage (HTML and terminal reports)
- `uv run pytest` - Run tests without coverage
- `uv run pytest tests/test_specific.py` - Run a single test file

### Code Quality
- `make format` - Format code using ruff
- `make mypy` - Run type checking with mypy
- `uvx ruff format` - Format code directly
- `uv run mypy .` - Type check the entire project

## Project Structure

- `src/` - Main source code directory
- `tests/` - Test files following pytest conventions
- `data/` - Data files for the project
- `htmlcov/` - Coverage reports (generated)
- `notes.md` - Development notes and ideas

## Dependencies and Tools

- **Package Manager**: uv (modern Python package manager)
- **Testing**: pytest with coverage reporting
- **Formatting**: ruff
- **Type Checking**: mypy
- **Key Libraries**: loguru, pydantic, typer

## Testing Configuration

- Tests are in the `tests/` directory
- Coverage configured to track `src/` directory
- HTML coverage reports generated in `htmlcov/`
- pytest.ini configures test discovery and output formatting

## Standard Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.