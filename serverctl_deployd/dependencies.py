"""
Miscellaneous dependencies for the API.
"""


import docker
from docker.client import DockerClient


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
