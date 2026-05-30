from collections.abc import Collection, Sequence
from typing import Any

from tests.integration.api_client import APIResponse


def assert_one_success_one_error(
    responses: Sequence[APIResponse[Any]],
    expected_errors: Collection[tuple[int, str]],
) -> None:
    """Assert that a two-request race returned one success and one expected error."""
    assert len(responses) == 2

    successes = [response for response in responses if response.status == 200]
    errors = [response for response in responses if response.status != 200]

    assert len(successes) == 1
    assert len(errors) == 1
    errors[0].assert_error_in(expected_errors)
