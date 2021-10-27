"""
Miscellaneous dependencies for the API.
"""


from functools import lru_cache

import docker
from docker.client import DockerClient

from serverctl_deployd.config import Settings


async def check_authentication() -> None:
    """
    TODO: To be implemented
    """
    pass  # pylint: disable=unnecessary-pass


async def get_docker_client() -> DockerClient:
    """
    Get the Docker client.
    """
    return docker.from_env()   # pragma: no cover


@lru_cache()
def get_settings() -> Settings:
    """
    Return settings to be used as a dependency.
    This is only there so that it can be overridden for tests.
    """
    return Settings()
