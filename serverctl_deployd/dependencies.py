"""
Miscellaneous dependencies for the API.
"""


import os
from functools import lru_cache
from pathlib import Path

import docker
from docker.client import DockerClient
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from pydantic.types import FilePath

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


def deployments_data_file(
    settings: Settings = Depends(get_settings)
) -> FilePath:
    """
    Return deployments data file.
    """
    data_file: str = os.path.join(
        settings.data_files_dir,
        "deployments.json"
    )
    file_path = Path(data_file)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployments data does not exist"
        )
    return file_path
