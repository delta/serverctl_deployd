"""
Router for Docker routes
"""

from docker import DockerClient
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from docker.types.daemon import CancellableStream
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import StreamingResponse

from serverctl_deployd.dependencies import get_docker_client
from serverctl_deployd.models.docker import PruneRequest, PruneResponse
from serverctl_deployd.models.exceptions import GenericError

router = APIRouter(
    prefix="/docker",
    tags=["docker"]
)


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
