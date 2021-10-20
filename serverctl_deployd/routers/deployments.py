"""
Router for Deployment routes
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic.types import FilePath
from starlette.responses import Response

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import deployments_data_file, get_settings
from serverctl_deployd.models.deployments import (Deployment, NamedDeployment,
                                                  UpdateDeployment)
from serverctl_deployd.models.exceptions import GenericError


def _merge_dicts(
    current: Dict[Any, Any],
    update: Dict[Any, Any],
    path: Optional[List[str]] = None
) -> Dict[Any, Any]:
    """
    Merges two dicts: update into current.
    Used for update_deployment()
    """
    if path is None:
        path = []
    for key in update:
        if key in current:
            if isinstance(current[key], dict) and isinstance(
                    update[key], dict):
                _merge_dicts(current[key], update[key], path + [str(key)])
            elif current[key] == update[key]:
                pass
            else:
                current[key] = update[key]
        else:
            current[key] = update[key]
    return current


router: APIRouter = APIRouter(
    prefix="/deployments",
    tags=["deployments"]
)


@router.post(
    "/",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": GenericError},
        status.HTTP_409_CONFLICT: {"model": GenericError}
    },
    response_model=NamedDeployment
)
def create_deployment(
    deployment: NamedDeployment,
    settings: Settings = Depends(get_settings)
) -> NamedDeployment:
    """Create a deployment"""
    try:
        subprocess.run(
            ["docker-compose", "-f", deployment.compose_path, "config"],
            check=True,
            stdout=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as called_process_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid docker-compose file"
        ) from called_process_error

    data_file: str = os.path.join(
        settings.data_files_dir,
        "deployments.json"
    )
    Path(settings.data_files_dir).mkdir(parents=True, exist_ok=True)
    Path(data_file).touch()

    with open(data_file, "r+", encoding="utf-8") as json_file:
        if Path(data_file).stat().st_size == 0:
            init_json: Dict[str, Any] = {}
            json.dump(init_json, json_file)
            json_file.seek(0)

        json_data = json.load(json_file)

        if deployment.name in json_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A deployment with same name already exists"
            )

        deployment_json = jsonable_encoder(deployment)
        del deployment_json["name"]
        json_data[deployment.name] = deployment_json
        json_file.seek(0)
        json.dump(json_data, json_file, indent=4)
    return deployment


@router.get(
    "/",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    response_model=Dict[str, Deployment]
)
def get_deployments(
    data_file: FilePath = Depends(deployments_data_file)
) -> Any:
    """Get a JSON of all deployments"""
    with open(data_file, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        return json_data


@router.get(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    response_model=Deployment
)
def get_deployment(
    name: str,
    data_file: FilePath = Depends(deployments_data_file)
) -> Any:
    """Get details of a deployment"""
    with open(data_file, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        if name not in json_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment does not exist"
            )
        return json_data[name]


@router.patch(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": GenericError}
    },
    response_model=UpdateDeployment
)
def update_deployment(
    name: str,
    deployment: UpdateDeployment,
    data_file: FilePath = Depends(deployments_data_file)
) -> UpdateDeployment:
    """Update a deployment"""
    with open(data_file, "r+", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        if name not in json_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment does not exist"
            )

        if deployment.compose_path:
            try:
                subprocess.run(
                    ["docker-compose", "-f", deployment.compose_path, "config"],
                    check=True,
                    stdout=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as called_process_error:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid docker-compose file"
                ) from called_process_error

        current_details = json_data[name]
        current_deployment = UpdateDeployment(**current_details)
        updated_details = _merge_dicts(current_details,
                                       deployment.dict(exclude_unset=True))
        updated_deployment = current_deployment.copy(update=updated_details)

        json_data[name] = jsonable_encoder(updated_deployment)
        json_file.seek(0)
        json.dump(json_data, json_file, indent=4)
        json_file.truncate()
        return updated_deployment


@router.delete(
    "/{name}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    },
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_deployment(
    name: str,
    data_file: FilePath = Depends(deployments_data_file)
) -> Response:
    """Delete a deployment"""
    with open(data_file, "r+", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        if name not in json_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment does not exist"
            )
        del json_data[name]
        json_file.seek(0)
        json.dump(json_data, json_file, indent=4)
        json_file.truncate()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{name}/up",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    }
)
def compose_up(
    name: str,
    data_file: FilePath = Depends(deployments_data_file)
) -> Dict[str, str]:
    """docker-compose up"""
    with open(data_file, "r+", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        if name not in json_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment does not exist"
            )
        compose_file = json_data[name]["compose_path"]
    try:
        subprocess.Popen(  # pylint: disable=consider-using-with
            ["docker-compose", "-f", compose_file, "up", "-d"],
            stdout=subprocess.DEVNULL
        )
    except OSError as os_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from os_error
    return {"message": "docker-compose up executed"}


@router.post(
    "/{name}/down",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError}
    }
)
def compose_down(
    name: str,
    data_file: FilePath = Depends(deployments_data_file)
) -> Dict[str, str]:
    """docker-compose down"""
    with open(data_file, "r+", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        if name not in json_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deployment does not exist"
            )
        compose_file = json_data[name]["compose_path"]
    try:
        subprocess.Popen(  # pylint: disable=consider-using-with
            ["docker-compose", "-f", compose_file, "down"],
            stdout=subprocess.DEVNULL
        )
    except OSError as os_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from os_error
    return {"message": "docker-compose down executed"}
