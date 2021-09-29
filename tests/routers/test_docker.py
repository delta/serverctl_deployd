"""
Tests for the Docker API routes
"""

from unittest.mock import PropertyMock, patch

import pytest
from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response
from docker.client import DockerClient
from docker.errors import APIError, ImageNotFound, NotFound
from fastapi import status

from serverctl_deployd.dependencies import get_docker_client
from serverctl_deployd.main import app
from serverctl_deployd.models.docker import (BuildCachesDeleted,
                                             ContainerDetails,
                                             ContainersDeleted, ImagesDeleted,
                                             LogsResponse, NetworksDeleted,
                                             PruneResponse, VolumesDeleted)
from tests.fakes.fake_docker_api import (FAKE_CONTAINER_ID,
                                         FAKE_CONTAINER_NAME, FAKE_IMAGE_ID,
                                         FAKE_LOG_LINE_CONTENT,
                                         FAKE_LOG_LINE_COUNT,
                                         FAKE_LOGS_MESSAGE, FAKE_LONG_ID,
                                         FAKE_TAG)
from tests.fakes.fake_docker_client import make_fake_client


async def _get_fake_docker_client() -> DockerClient:
    return make_fake_client()


app.dependency_overrides[get_docker_client] = _get_fake_docker_client


@pytest.mark.asyncio
async def test_docker_prune() -> None:
    """Test the docker prune endpoint"""

    async with TestClient(app) as client:

        # Test successful prune all
        response: Response = await client.post("/docker/prune", json={"all": True})
        assert response.status_code == status.HTTP_200_OK
        prune_response = PruneResponse.parse_obj(response.json())
        assert isinstance(prune_response.containers, ContainersDeleted)
        assert prune_response.containers.containers_deleted[0] == FAKE_LONG_ID
        assert isinstance(prune_response.images, ImagesDeleted)
        assert prune_response.images.images_deleted[0] == FAKE_LONG_ID
        assert isinstance(prune_response.volumes, VolumesDeleted)
        assert prune_response.volumes.volumes_deleted[0] == FAKE_LONG_ID
        assert isinstance(prune_response.networks, NetworksDeleted)
        assert prune_response.networks.networks_deleted[0] == FAKE_LONG_ID
        assert isinstance(prune_response.build_cache, BuildCachesDeleted)
        assert prune_response.build_cache.caches_deleted[0] == FAKE_LONG_ID

        # Test successful prune only containers
        response = await client.post("/docker/prune", json={"containers": True})
        assert response.status_code == status.HTTP_200_OK
        prune_response = PruneResponse.parse_obj(response.json())
        assert isinstance(prune_response.containers, ContainersDeleted)
        assert prune_response.containers.containers_deleted[0] == FAKE_LONG_ID
        assert prune_response.images is None
        assert prune_response.volumes is None
        assert prune_response.networks is None
        assert prune_response.build_cache is None

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.prune.side_effect = APIError("API error")
            response = await client.post("/docker/prune", json={"containers": True})
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


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
                "/docker/containers/wrong_id/attach")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.get(
                f"/docker/containers/{FAKE_CONTAINER_ID}/attach")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_get_containers() -> None:
    """Test the docker get containers endpoint"""

    async with TestClient(app) as client:

        # Test successful get containers
        containers: Response = await client.get("/docker/containers")
        assert containers.status_code == status.HTTP_200_OK
        for container in containers.json():
            # pylint: disable-next=fixme
            # TODO: Fix the test as image name is not being returned currently
            container_details = ContainerDetails.parse_obj(container)
            assert container_details.id == FAKE_CONTAINER_ID
            assert container_details.name == FAKE_CONTAINER_NAME
            assert isinstance(container_details, ContainerDetails)

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.list.side_effect = APIError("API Error")
            response = await client.get("/docker/containers")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_get_container_details() -> None:
    """Test the docker get container details endpoint"""

    async with TestClient(app) as client:

        # Test successful get container details
        container_details: Response = await client.get(
            f"/docker/containers/{FAKE_CONTAINER_ID}")
        assert container_details.status_code == status.HTTP_200_OK
        container_details = ContainerDetails.parse_obj(
            container_details.json())
        assert container_details.id == FAKE_CONTAINER_ID
        assert container_details.name == FAKE_CONTAINER_NAME
        assert isinstance(container_details, ContainerDetails)

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.get(
                f"/docker/containers/{FAKE_CONTAINER_ID}")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.get(
                f"/docker/containers/{FAKE_CONTAINER_ID}")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_delete() -> None:
    """Test the docker post container delete endpoint"""

    async with TestClient(app) as client:

        # Test successful delete container
        response: Response = await client.post(
            "/docker/containers/delete",
            json={
                "container_id": FAKE_CONTAINER_ID
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[
            "message"] == f"Container {FAKE_CONTAINER_ID} deleted"

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.post(
                "/docker/containers/delete",
                json={
                    "container_id": FAKE_CONTAINER_ID
                }
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails as container can't be removed
        with patch("docker.models.containers.Container.remove") as container_remove,\
            patch(
                "docker.models.containers.Container.status",
                new_callable=PropertyMock
        ) as container_status:
            container_remove.side_effect = APIError("API Error")
            container_status.return_value = "running"
            response = await client.post(
                "/docker/containers/delete",
                json={
                    "container_id": FAKE_CONTAINER_ID
                }
            )
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()[
                "detail"] == "Cannot remove running containers, try forcing"

        # Test condition where Docker API fails
        with patch("docker.models.containers.Container.remove") as container_remove,\
            patch(
                "docker.models.containers.Container.status",
                new_callable=PropertyMock
        ) as container_status:
            container_remove.side_effect = APIError("API Error")
            container_status.return_value = "exited"
            response = await client.post(
                "/docker/containers/delete",
                json={
                    "container_id": FAKE_CONTAINER_ID
                }
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_start() -> None:
    """Test the docker post container start endpoint"""

    async with TestClient(app) as client:

        # Test successful start container
        response: Response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/start")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[
            "message"] == f"Container {FAKE_CONTAINER_ID} started"

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/start")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/start")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_stop() -> None:
    """Test the docker post container stop endpoint"""

    async with TestClient(app) as client:

        # Test successful stop container
        response: Response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/stop")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[
            "message"] == f"Container {FAKE_CONTAINER_ID} stopped"

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/stop")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/stop")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_restart() -> None:
    """Test the docker post container restart endpoint"""

    async with TestClient(app) as client:

        # Test successful restart container
        response: Response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/restart")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[
            "message"] == f"Container {FAKE_CONTAINER_ID} restarted"

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/restart")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/restart")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_kill() -> None:
    """Test the docker post kill container endpoint"""
    async with TestClient(app) as client:

        # Test successful kill container
        response: Response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/kill")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[
            "message"] == f"Container {FAKE_CONTAINER_ID} killed"

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/kill")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails as container is not running
        with patch("docker.models.containers.Container.kill") as container_kill,\
            patch(
                "docker.models.containers.Container.status",
                new_callable=PropertyMock
        ) as container_status:
            container_kill.side_effect = APIError("API Error")
            container_status.return_value = "exited"
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/kill")
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()[
                "detail"] == "Cannot kill containers that are not running"

        # Test condition where Docker API fails
        with patch("docker.models.containers.Container.kill") as container_kill,\
            patch(
                "docker.models.containers.Container.status",
                new_callable=PropertyMock
        ) as container_status:
            container_kill.side_effect = APIError("API Error")
            container_status.return_value = "running"
            response = await client.post(f"/docker/containers/{FAKE_CONTAINER_ID}/kill")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_container_logs() -> None:
    """Test get container logs endpoint"""
    async with TestClient(app) as client:

        # Test successful get container logs
        response: Response = await client.get(f"/docker/containers/{FAKE_CONTAINER_ID}/logs")
        logs_response = LogsResponse.parse_obj(response.json())
        assert logs_response.container_id == FAKE_CONTAINER_ID
        assert logs_response.logs == FAKE_LOGS_MESSAGE

        # Test condition where container does not exist
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = NotFound("Not found")
            response = await client.get(f"/docker/containers/{FAKE_CONTAINER_ID}/logs")
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Container not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "containers") as containers:
            containers.get.side_effect = APIError("API Error")
            response = await client.get(f"/docker/containers/{FAKE_CONTAINER_ID}/logs")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"


@pytest.mark.asyncio
async def test_docker_post_tag_image() -> None:
    """Test post tag image endpoint"""
    async with TestClient(app) as client:

        # Test successful tag image
        response: Response = await client.post("/docker/images/tag", json={
            "image_id": FAKE_IMAGE_ID,
            "tag": FAKE_TAG
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == f"Image {FAKE_IMAGE_ID} tagged"

        # Test condition where image does not exist
        with patch.object(DockerClient, "images") as images:
            images.get.side_effect = ImageNotFound("Not found")
            response = await client.post("/docker/images/tag", json={
                "image_id": FAKE_IMAGE_ID,
                "tag": FAKE_TAG
            })
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["detail"] == "Image not found"

        # Test condition where Docker API fails
        with patch.object(DockerClient, "images") as images:
            images.get.side_effect = APIError("API Error")
            response = await client.post("/docker/images/tag", json={
                "image_id": FAKE_IMAGE_ID,
                "tag": FAKE_TAG
            })
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Internal server error"
