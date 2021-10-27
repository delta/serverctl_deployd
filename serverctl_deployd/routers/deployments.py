"""
Router for Deployment routes
"""

import json
import shlex
import subprocess
from os import path, scandir
from shutil import rmtree
from typing import Any, Dict, Set

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette.responses import Response

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import get_settings
from serverctl_deployd.models.deployments import (DBConfig, Deployment,
                                                  UpdateDeployment)
from serverctl_deployd.models.exceptions import GenericError


def _merge_dicts(
    current: Dict[Any, Any],
    update: Dict[Any, Any]
) -> Dict[Any, Any]:
    """
    Merges two dicts: update into current.
    Used for update_deployment()
    """
    for key in update:
        if key in current:
            if isinstance(current[key], dict) and isinstance(
                    update[key], dict):
                _merge_dicts(current[key], update[key])
            elif update[key] and current[key] != update[key]:
                current[key] = update[key]
    return current


router: APIRouter = APIRouter(
    prefix="/deployments",
    tags=["deployments"]
)


@router.post(
    "/",
    responses={
        status.HTTP_409_CONFLICT: {"model": GenericError}
    },
    response_model=Deployment,
)
def create_deployment(
    deployment: Deployment,
    settings: Settings = Depends(get_settings)
) -> Deployment:
    """Create a deployment"""
    deployment_path = settings.deployments_dir.joinpath(deployment.name)
    try:
        deployment_path.mkdir(parents=True)
    except FileExistsError as dir_exists_error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A deployment with same name already exists"
        ) from dir_exists_error

    compose_path = deployment_path.joinpath("docker-compose.yml")
    compose_path.write_text(deployment.compose_file,
                            encoding="utf-8")

    if deployment.env_file:
        env_path = deployment_path.joinpath(".env")
        env_path.write_text(deployment.env_file,
                            encoding="utf-8")

    if deployment.databases:
        db_file = deployment_path.joinpath("databases.json")
        db_file.touch()

        with open(db_file, "w", encoding="utf-8") as json_file:
            db_json = jsonable_encoder(deployment.databases)
            json.dump(db_json, json_file, indent=4)

    return deployment


@router.get("/", response_model=Set[str])
def get_deployments(
    settings: Settings = Depends(get_settings)
) -> Set[str]:
    """Get a list of all deployments"""
    deployments: Set[str] = set()
    if settings.deployments_dir.exists():
        deployments.update(
            item.name for item in scandir(settings.deployments_dir)
            if item.is_dir())
    return deployments


@router.get(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    response_model=Dict[str, DBConfig]
)
def get_deployment(
    name: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, DBConfig]:
    """Get database details of a deployment"""
    deployment_path = settings.deployments_dir.joinpath(name)
    if not deployment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment does not exist"
        )
    db_file = deployment_path.joinpath("databases.json")
    json_data: Dict[str, DBConfig] = {}
    if db_file.exists():
        with open(db_file, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
    return json_data


@ router.patch(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    status_code=status.HTTP_204_NO_CONTENT
)
def update_deployment(
    name: str,
    update: UpdateDeployment,
    settings: Settings = Depends(get_settings)
) -> Response:
    """Update a deployment"""
    deployment_path = settings.deployments_dir.joinpath(name)
    if not deployment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment does not exist"
        )

    if update.compose_file:
        compose_path = deployment_path.joinpath("docker-compose.yml")
        compose_path.write_text(update.compose_file,
                                encoding="utf-8")

    if update.env_file:
        env_path = deployment_path.joinpath(".env")
        env_path.write_text(update.env_file,
                            encoding="utf-8")

    if update.databases:
        db_file = deployment_path.joinpath("databases.json")
        db_file.touch()

        with open(db_file, "r+", encoding="utf-8") as json_file:
            current_details = json.load(json_file)
            update_json = jsonable_encoder(update.databases)
            updated_details = _merge_dicts(current_details,
                                           update_json)
            json_file.seek(0)
            json.dump(updated_details, json_file, indent=4)
            json_file.truncate()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@ router.delete(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_deployment(
    name: str,
    settings: Settings = Depends(get_settings)
) -> Response:
    """Delete a deployment"""
    deployment_path = settings.deployments_dir.joinpath(name)
    if not deployment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment does not exist"
        )
    rmtree(deployment_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@ router.post(
    "/{name}/up",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    },
    response_model=Dict[str, str]
)
def compose_up(
    name: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """docker-compose up"""
    deployment_path = settings.deployments_dir.joinpath(name)
    if not deployment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment does not exist"
        )
    compose_path = path.join(deployment_path, "docker-compose.yml")
    try:
        subprocess.Popen(  # pylint: disable=consider-using-with
            f"docker-compose -f {shlex.quote(compose_path)} up -d &",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError as os_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from os_error
    return {"message": "docker-compose up executed"}


@ router.post(
    "/{name}/down",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
def compose_down(
    name: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """docker-compose down"""
    deployment_path = settings.deployments_dir.joinpath(name)
    if not deployment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment does not exist"
        )
    compose_path = path.join(deployment_path, "docker-compose.yml")
    try:
        subprocess.Popen(  # pylint: disable=consider-using-with
            f"docker-compose -f {shlex.quote(compose_path)} down &",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError as os_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from os_error
    return {"message": "docker-compose down executed"}
