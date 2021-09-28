"""
Router for Docker routes
"""

import logging
from typing import Dict, List

from docker import DockerClient
from docker.errors import APIError, ImageNotFound, NotFound
from docker.models.containers import Container, Image
from docker.types.daemon import CancellableStream
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import StreamingResponse

from serverctl_deployd.dependencies import get_docker_client
from serverctl_deployd.models.docker import (ContainerDetails, DeleteRequest,
                                             ImageTagRequest, LogsResponse,
                                             PruneRequest, PruneResponse)
from serverctl_deployd.models.exceptions import GenericError

router = APIRouter(
    prefix="/docker",
    tags=["docker"]
)

@router.get(
    "/containers/{container_id}",
    response_model = ContainerDetails,
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def get_container_details(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> ContainerDetails:
    """
    Get container details
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container_response: ContainerDetails = ContainerDetails(
            id = container.id,
            status = container.status,
            image = container.image.tags,
            name = container.name,
            ports = container.ports,
            created = container.attrs['Created'])

    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found"
        ) from not_found_exception
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception
    return container_response

@router.post(
    "/containers/delete",
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_403_FORBIDDEN: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def delete_container(
    delete_request: DeleteRequest,
    docker_client: DockerClient = Depends(get_docker_client)
) -> Dict[str, str]:
    """
    Delete container
    """
    container = Container()
    try:
        container = docker_client.containers.get(delete_request.container_id)
        container.remove(force=delete_request.force, v=delete_request.v)
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        if container.status == "running":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove running containers, try forcing") from api_error_exception
        logging.exception("Error deleting the container %s", delete_request.container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return { "message": f"Container {delete_request.container_id} deleted" }

@router.post(
    "/containers/{container_id}/start",
    responses = {
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def start_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> Dict[str, str]:
    """
    Start container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.start()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error starting the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return { "message": f"Container {container_id} started" }

@router.post(
    "/containers/{container_id}/stop",
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
})
async def stop_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> Dict[str, str]:
    """
    Stop container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.stop()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error stopping the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return { "message": f"Container {container_id} stopped" }

@router.post(
    "/containers/{container_id}/restart",
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
})
async def restart_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> Dict[str, str]:
    """
    Restart container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.restart()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error restarting the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return { "message": f"Container {container_id} restarted" }

@router.post(
    "/containers/{container_id}/kill",
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_403_FORBIDDEN: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
})
async def kill_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> Dict[str, str]:
    """
    Kill container
    """
    container = Container()
    try:
        container = docker_client.containers.get(container_id)
        container.kill()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        if container.status != "running":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot kill containers that are not running") from api_error_exception
        logging.exception("Error killing the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return { "message": f"Container {container_id} killed" }

@router.get(
    "/containers/{container_id}/logs",
    response_model = LogsResponse,
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
})
async def get_logs(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> LogsResponse:
    """
    Get logs
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        logs: str = container.logs()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error getting the logs of the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return LogsResponse(container_id = container_id ,logs=logs)

@router.get("/containers",
    response_model = List[ContainerDetails],
    responses = {
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def get_containers(
    docker_client: DockerClient = Depends(get_docker_client)
    ) -> List[ContainerDetails]:
    """
    Get all containers
    """
    try:
        containers: List[Container] = [ContainerDetails(
            id = container.id,
            status = container.status,
            image = container.image.tags,
            name = container.name,
            ports = container.ports,
            created = container.attrs['Created']
            )
            for container in docker_client.containers.list(all=True)]
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
            ) from api_error_exception
    return containers

@router.post(
    "/images/tag",
    responses = {
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    })
async def tag_image(
    tag_image_request: ImageTagRequest,
    docker_client: DockerClient = Depends(get_docker_client)
    ) -> Dict[str, str]:
    """
    Tag image
    """
    try:
        image: Image = docker_client.images.get(tag_image_request.image_id)
        image.tag(tag_image_request.tag, "latest")
    except ImageNotFound as image_not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        ) from image_not_found_exception
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception
    return { "message": f"Image {tag_image_request.image_id} tagged" }

@router.post(
    "/prune",
    response_model=PruneResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def prune(
    prune_request: PruneRequest,
    docker_client: DockerClient = Depends(get_docker_client)
) -> PruneResponse:
    """
    Prune Docker images and containers
    """
    try:
        prune_response = PruneResponse()
        if prune_request.containers or prune_request.all:
            prune_response.containers = docker_client.containers.prune()
        if prune_request.images or prune_request.all:
            prune_response.images = docker_client.images.prune()
        if prune_request.volumes or prune_request.all:
            prune_response.volumes = docker_client.volumes.prune()
        if prune_request.networks or prune_request.all:
            prune_response.networks = docker_client.networks.prune()
        if prune_request.build_cache or prune_request.all:
            prune_response.build_cache = docker_client.api.prune_builds()
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception
    return prune_response


@router.get(
    "/containers/{container_id}/attach",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def container_attach(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker_client)
) -> StreamingResponse:
    """
    Returns a HTTP Stream for the container's stdout and stderr
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        log_stream: CancellableStream = container.attach(stream=True)
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found"
        ) from not_found_exception
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception
    return StreamingResponse(
        log_stream,
        media_type="text/plain"
    )
