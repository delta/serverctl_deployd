"""
Router for Config routes
"""

import subprocess
import tarfile
from fnmatch import fnmatch
from hashlib import sha256
from io import BytesIO
from os import DirEntry, scandir
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, Body, File, status
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from pydantic.types import DirectoryPath, FilePath
from starlette.responses import Response

from serverctl_deployd.models.config import ConfigBucket, ListConfigBucket
from serverctl_deployd.models.exceptions import GenericError


def _list_files(path: DirectoryPath,
                patterns: Optional[Set[str]]) -> List[DirEntry[str]]:
    """
    Get a list of DirEntry objects for a path,
    to be used by other functions
    """
    file_list: List[DirEntry[str]] = []
    with scandir(path) as listing:
        for entry in listing:
            if entry.is_file():
                if not patterns or not any(
                    fnmatch(entry.name, pattern)
                    for pattern in patterns
                ):
                    file_list.append(entry)
    return file_list


def _get_hashes(path: DirectoryPath,
                patterns: Optional[Set[str]]) -> Dict[str, str]:
    """
    Get hashes of files in a directory whose file names do not
    match the glob patterns
    """
    file_hash_list: Dict[str, str] = {}
    for entry in _list_files(path, patterns):
        file_hash = sha256()
        byte_array = bytearray(128 * 1024)
        memory_view = memoryview(byte_array)
        with open(entry.path, 'rb', buffering=0) as conf_file:
            for buffer_size in iter(
                lambda cf=conf_file, mv=memory_view:  # type: ignore
                cf.readinto(mv), 0
            ):
                file_hash.update(memory_view[:buffer_size])
        file_hash_str = file_hash.hexdigest()
        file_hash_list.update({entry.name: file_hash_str})
    return file_hash_list


router = APIRouter(
    prefix="/config/buckets",
    tags=["config"]
)


@router.post(
    "/",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    },
    response_model=Dict[str, str]
)
def validate_bucket(config_bucket: ConfigBucket) -> Dict[str, str]:
    """
    Checks if the directory path and config updation command are valid.
    If valid then returns a list of files and its hashes
    """
    if config_bucket.update_command:
        try:
            subprocess.run(
                config_bucket.update_command,
                shell=True,
                executable="/bin/bash",
                check=True
            )
        except subprocess.SubprocessError as execution_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) from execution_error
    return _get_hashes(
        config_bucket.directory_path,
        config_bucket.ignore_patterns
    )


@router.post("/files", response_model=List[str])
def list_filenames(config_bucket: ListConfigBucket) -> List[str]:
    """Return list of file names for a config bucket"""
    filename_list = [
        entry.name for entry in _list_files(
            config_bucket.directory_path,
            config_bucket.ignore_patterns
        )
    ]
    return filename_list


@router.post("/check", response_model=Dict[str, str])
def get_hashes(config_bucket: ListConfigBucket) -> Dict[str, str]:
    """
    Return list of file names for a bucket and their sha256 checksums
    which will be verified by the serverctl API
    """
    return _get_hashes(
        config_bucket.directory_path,
        config_bucket.ignore_patterns
    )


@router.post(
    "/backup",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/x-tar": {}}
        }
    },
    response_class=Response
)
def get_tar_archive(
    config_bucket: ListConfigBucket
) -> Response:
    """Returns the tar archive of config folder for backup"""
    file_list = _list_files(
        config_bucket.directory_path,
        config_bucket.ignore_patterns
    )
    size = sum(entry.stat().st_size for entry in file_list)
    byte_array = bytearray(size)
    file_object = BytesIO(byte_array)
    with tarfile.open(mode="w:gz", fileobj=file_object) as tar_file:
        for entry in file_list:
            tar_file.add(entry.path, arcname=entry.name)
    return Response(
        content=file_object.getvalue(),
        media_type="application/x-tar"
    )


@router.get(
    "/file", response_class=FileResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"text/plain": {}}
        }
    }
)
async def get_file(file_path: FilePath) -> FileResponse:
    """Returns the requested config file"""
    return FileResponse(file_path)


@router.put(
    "/file", response_class=FileResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"text/plain": {}}
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def update_file(
    file_path: FilePath,
    update_command: str = Body(...),
    new_file: UploadFile = File(...)
) -> FileResponse:
    """Updates the requested config file"""
    new_content: Any = await new_file.read()
    file_path.write_bytes(new_content)
    try:
        subprocess.run(
            update_command,
            shell=True,
            executable="/bin/bash",
            check=True
        )
    except subprocess.SubprocessError as execution_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from execution_error
    return FileResponse(file_path)


@router.delete(
    "/file",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    },
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_file(
    file_path: FilePath,
    update_command: str = Body(..., embed=True)
) -> Response:
    """Deletes the requested config file"""
    file_path.unlink()
    try:
        subprocess.run(
            update_command,
            shell=True,
            executable="/bin/bash",
            check=True
        )
    except subprocess.SubprocessError as execution_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from execution_error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
