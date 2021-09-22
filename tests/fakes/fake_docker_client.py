"""
Fake Docker API client

Adapted from https://github.com/docker/docker-py/blob/master/tests/unit/fake_api_client.py
"""

import copy
from typing import Any
from unittest import mock

import docker

from . import fake_docker_api as fake_api


class CopyReturnMagicMock(mock.MagicMock):
    """
    A MagicMock which deep copies every return value.
    """

    def _mock_call(self, *args: str, **kwargs: int) -> Any:
        ret = super()._mock_call(*args, **kwargs)
        if isinstance(ret, (dict, list)):
            ret = copy.deepcopy(ret)
        return ret


def _make_fake_api_client() -> docker.APIClient:
    api_client = docker.APIClient()
    mock_attrs = {
        "containers.return_value": fake_api.get_fake_containers()[1],
        "attach.return_value": fake_api.get_fake_logs()[1],
        "inspect_container.return_value":
            fake_api.get_fake_inspect_container()[1],
        "create_host_config.side_effect": api_client.create_host_config,
    }
    mock_client = CopyReturnMagicMock(**mock_attrs)
    return mock_client


def make_fake_client() -> docker.DockerClient:
    """
    Returns a Client with a fake APIClient.
    """
    client = docker.DockerClient()
    client.api = _make_fake_api_client()
    return client
