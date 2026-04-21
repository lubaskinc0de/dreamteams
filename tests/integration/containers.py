"""Custom testcontainer wrappers for infrastructure not covered by the ``testcontainers`` extras."""

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

RUSTFS_ACCESS_KEY = "rustfsadmin"
RUSTFS_SECRET_KEY = "rustfsadmin"
RUSTFS_S3_PORT = 9000


class RustFsContainer(DockerContainer):  # type: ignore[misc]
    """Testcontainer wrapper around the rustfs S3-compatible storage image used by the API in prod."""

    def __init__(
        self,
        image: str = "rustfs/rustfs:1.0.0-alpha.82",
        access_key: str = RUSTFS_ACCESS_KEY,
        secret_key: str = RUSTFS_SECRET_KEY,
    ) -> None:
        super().__init__(image)
        self.access_key = access_key
        self.secret_key = secret_key
        self.with_exposed_ports(RUSTFS_S3_PORT)
        self.with_env("RUSTFS_ACCESS_KEY", access_key)
        self.with_env("RUSTFS_SECRET_KEY", secret_key)
        # Any HTTP reply proves the S3 port is serving; rustfs returns 403 on `/` without auth.
        self.waiting_for(HttpWaitStrategy(RUSTFS_S3_PORT).for_status_code_matching(lambda _code: True))

    def get_endpoint_url(self) -> str:
        """Resolve the S3 endpoint URL (host + host-mapped container port)."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(RUSTFS_S3_PORT)
        return f"http://{host}:{port}"
