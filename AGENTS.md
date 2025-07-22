# Project Instructions

This repository contains a React frontend, a FastAPI backend, and Azure deployment scripts.
The application uses SQLite locally and Azure Cosmos DB when `ENV=azure`.

## Coding guidelines
- Python 3.11
- Follow PEP 8 with 4 space indentation and a 120 character line length limit.
- Use Google style docstrings for all functions and classes.
- Name files and functions in `snake_case` and classes in `PascalCase`.

## Programmatic checks
Run the following commands before committing:
1. `python -m py_compile $(git ls-files '*.py')`
2. `pytest` from the `backend` directory (tests may be empty)
3. If dependencies are installed, `npm run build` inside `frontend` to ensure the React app compiles.

## Documentation
Update `README.md` and any relevant docs when changing features or architecture.

## Commit messages
Use short, imperative commit messages summarizing the change.
