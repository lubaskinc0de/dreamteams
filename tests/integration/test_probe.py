from tests.integration.api_client import ApiClient


async def test_alive(api_client: ApiClient) -> None:
    """Test liveness probe."""
    response = await api_client.liveness()

    response.assert_status(200).ensure_content()


async def test_readiness(api_client: ApiClient) -> None:
    """Test readiness probe."""
    response = await api_client.readiness()

    response.assert_status(200).ensure_content()
