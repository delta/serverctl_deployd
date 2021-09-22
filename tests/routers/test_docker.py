"""
Tests for the Docker API routes
"""

from unittest.mock import patch

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from docker.client import DockerClient
from docker.errors import APIError, NotFound
from fastapi import status

from serverctl_deployd.dependencies import get_docker_client
from serverctl_deployd.main import app
from tests.fakes.fake_docker_api import (FAKE_CONTAINER_ID,
                                         FAKE_LOG_LINE_CONTENT,
                                         FAKE_LOG_LINE_COUNT)
from tests.fakes.fake_docker_client import make_fake_client


async def _get_fake_docker_client() -> DockerClient:
    return make_fake_client()


app.dependency_overrides[get_docker_client] = _get_fake_docker_client


@pytest.mark.asyncio
async def test_docker_attach() -> None:
    """Test the docker attach endpoint"""

    async with TestClient(app) as client:

        # Test successful attach
        response: Response = await client.get(
            f"/docker/containers/{FAKE_CONTAINER_ID}/attach", stream=True)
        line_count = 0
        async for line in response.iter_content(chunk_size=512):
            if line:
                assert line == FAKE_LOG_LINE_CONTENT
                line_count += 1
        assert line_count == FAKE_LOG_LINE_COUNT

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.get(
                "/docker/containers/wrong_digest/attach")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.get(
                f"/docker/containers/{FAKE_CONTAINER_ID}/attach")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"
