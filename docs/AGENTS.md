# Agent Guidelines

This document defines rules and best practices for AI agents working on this project.

## Core Principles

### 1. Study the Project Thoroughly

-   Read existing code before making changes
-   Understand the project structure and architecture
-   Review documentation in `docs/` directory
-   Examine similar implementations in the codebase

### 2. Follow Existing Code Style

-   Maintain consistency with existing code patterns
-   Use the same naming conventions
-   Follow the same import order and structure
-   Match indentation and formatting style

### 3. Avoid Obvious Comments

-   Do not add comments for self-evident code
-   Code should be self-documenting through clear naming
-   Add comments only for complex business logic or non-obvious decisions
-   Docstrings are required for public APIs and entities

### 4. Search Before Implementing

-   Before implementing a feature, search for similar patterns in the codebase
-   Reuse existing abstractions and utilities
-   Follow established patterns

### 5. Python 3.13+

-   Use modern Python 3.13+ features
-   Type hints are mandatory

### 6. Architecture and code style

Follow clean architecture, SOLID, GRASP, DRY and KISS principles

### 7. Ask When Uncertain

-   If multiple approaches are valid, ask the user for preference
-   Clarify ambiguous requirements before implementing
-   Discuss architectural decisions that impact multiple components
-   Ask about trade-offs between different solutions

### 8. Verify Changes Work

After making changes, always run:

```bash
just lint  # Run linters (ruff, mypy)
just test  # Run test suite
```

Fix all linting errors and ensure tests pass before considering work complete.

## Code Style Specifics

## Documentation

-   docs/
-   Keep documentation concise and formal
-   Use English for all documentation
-   Focus on purpose, attributes, business rules, relationships

## What NOT to Do

-   ❌ Do not add features not requested by the user
-   ❌ Do not refactor working code without reason
-   ❌ Do not add comments for obvious code
-   ❌ Do not ignore linting errors
-   ❌ Do not skip running tests
-   ❌ Do not violate Clean Architecture boundaries
