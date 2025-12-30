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

### Docstrings

-   Keep docstrings concise and minimal
-   Avoid verbose multi-line docstrings with Args/Returns/Raises sections
-   Use single-line docstrings when possible
-   Let type annotations and code speak for themselves

### Logging

-   Always log `user_id` when available in the context
-   Include `user_id` in all log statements where user context exists

### Module Structure

-   Do not add imports or `__all__` exports to `__init__.py` files
-   Keep `__init__.py` files empty

### Testing

-   **Always prefer parametrization over creating multiple similar tests**
-   Use `@pytest.mark.parametrize` to combine tests that check the same behavior with different inputs
-   Never hardcode test values directly in assertions - use variables or parameters
-   Parametrized tests are more maintainable and easier to extend with new cases
-   Group related test cases together using parametrization instead of creating separate test functions

Example:

```python
# ❌ Bad - Multiple similar tests with hardcoded values
def test_max_zero_raises_error() -> None:
    with pytest.raises(Error):
        Limits(max=0, min=0)

def test_max_negative_raises_error() -> None:
    with pytest.raises(Error):
        Limits(max=-10, min=5)

# ✅ Good - Single parametrized test
@pytest.mark.parametrize(
    ("max_value", "min_value", "expected_error"),
    [
        (0, 0, "Max must be greater than 0"),
        (-10, 5, "Max must be greater than 0"),
    ],
)
def test_invalid_values_raise_error(max_value: int, min_value: int, expected_error: str) -> None:
    with pytest.raises(Error, match=expected_error):
        Limits(max=max_value, min=min_value)
```

### Use Case Registration

After implementing a use case, register it in the system:

1. **DI Container** (`bootstrap/di/providers/interactor.py`):
   - Import the interactor class
   - Add to `provide_all()` in `InteractorProvider.interactors`
   - Scope is already set to `Scope.REQUEST`

2. **FastAPI Route** (`presentation/fast_api/routers/`):
   - Create or update router file with `route_class=DishkaRoute`
   - Inject interactor via `FromDishka[InteractorClass]`
   - Can create separate Pydantic model for API if needed (transforms to interactor form)
   - Return interactor's response model directly

3. **Error Mapping** (`presentation/fast_api/error_handlers.py`):
   - Add new error types to `error_to_http_status` dict
   - Map error class to HTTP status code (400, 403, 404, 409, 422, etc.)

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
