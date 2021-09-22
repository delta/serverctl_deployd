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
from serverctl_deployd.models.exceptions import GenericError

router = APIRouter(
    prefix="/docker",
    tags=["docker"]
)


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
