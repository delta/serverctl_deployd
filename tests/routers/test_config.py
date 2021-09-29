"""
Tests for config management routes
"""

import filecmp
import os
import tarfile
from pathlib import Path
from shutil import rmtree

from fastapi.testclient import TestClient
from requests.models import Response

from serverctl_deployd.main import app
from tests.fakes.fake_config_directory import (MOCK_CONF_DIRPATH,
                                               MOCK_CONF_FILE_CONTENT,
                                               MOCK_CONF_FILEPATH,
                                               MOCK_CONF_NEW_CONTENT,
                                               MOCK_FILE_HASH,
                                               make_mock_config_dir)

client = TestClient(app)


def test_validate_bucket() -> None:
    """Test config bucket validation"""
    make_mock_config_dir()

    # Valid request
    response: Response = client.post(
        "/config/buckets/",
        json={
            "directory_path": MOCK_CONF_DIRPATH,
            "update_command": "echo updated",
            "ignore_patterns": ["leave*"]
        })
    assert response.status_code == 200
    assert response.json() == {
        "mock.conf": MOCK_FILE_HASH
    }

    # Unsuccessful or invalid command
    response = client.post(
        "/config/buckets/",
        json={
            "directory_path": MOCK_CONF_DIRPATH,
            "update_command": "invalid command",
            "ignore_patterns": ["leave*"]
        })
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error"
    }

    rmtree(MOCK_CONF_DIRPATH)


def test_list_filenames() -> None:
    """Test for file name list route i.e /files"""
    make_mock_config_dir()

    # Valid request
    response: Response = client.post(
        "/config/buckets/files",
        json={
            "directory_path": MOCK_CONF_DIRPATH,
            "ignore_patterns": ["leave*"]
        })
    assert response.status_code == 200
    assert response.json() == ["mock.conf"]

    rmtree(MOCK_CONF_DIRPATH)


def test_get_hashes() -> None:
    """Test for the get hashes route i.e /check"""
    make_mock_config_dir()

    # Valid request
    response: Response = client.post(
        "/config/buckets/check",
        json={
            "directory_path": MOCK_CONF_DIRPATH,
            "ignore_patterns": ["leave*"]
        })
    assert response.status_code == 200
    assert response.json() == {
        "mock.conf": MOCK_FILE_HASH
    }

    rmtree(MOCK_CONF_DIRPATH)


def test_get_file() -> None:
    """Test for getting config file"""
    make_mock_config_dir()

    # Valid request
    response: Response = client.get(
        "/config/buckets/file",
        params={"file_path": MOCK_CONF_FILEPATH}
    )
    assert response.status_code == 200
    assert response.content.decode() == MOCK_CONF_FILE_CONTENT

    rmtree(MOCK_CONF_DIRPATH)


def test_update_file() -> None:
    """Test for updating config file"""
    make_mock_config_dir()

    with open(
        MOCK_CONF_DIRPATH + "new_file.conf",
        'w', encoding="utf8"
    ) as new_file:
        new_file.write(MOCK_CONF_NEW_CONTENT)

    with open(
        MOCK_CONF_DIRPATH + "new_file.conf",
        'r', encoding="utf8"
    ) as new_file:
        # Valid request
        response: Response = client.put(
            "/config/buckets/file",
            params={"file_path": MOCK_CONF_FILEPATH},
            data={"update_command": "echo updated"},
            files={"new_file": new_file},
        )
        assert response.status_code == 200
        assert response.content.decode() == MOCK_CONF_NEW_CONTENT

        # Unsuccessful or invalid command
        response = client.put(
            "/config/buckets/file",
            params={"file_path": MOCK_CONF_FILEPATH},
            data={"update_command": "invalid command"},
            files={"new_file": new_file},
        )
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Internal server error"
        }

    rmtree(MOCK_CONF_DIRPATH)


def test_delete_file() -> None:
    """Test for deleting config file"""
    make_mock_config_dir()

    with open(
        MOCK_CONF_DIRPATH + "delete_this.conf",
        'w', encoding="utf8"
    ) as new_file:
        new_file.write(MOCK_CONF_FILE_CONTENT)

    # Valid request
    response: Response = client.delete(
        "/config/buckets/file",
        params={
            "file_path": MOCK_CONF_DIRPATH + "delete_this.conf"
        },
        json={"update_command": "echo updated"}
    )
    assert response.status_code == 204
    assert not Path(MOCK_CONF_DIRPATH + "delete_this.conf").is_file()

    with open(
        MOCK_CONF_DIRPATH + "delete_this.conf",
        'w', encoding="utf8"
    ) as new_file:
        new_file.write(MOCK_CONF_FILE_CONTENT)

    # Unsuccessful or invalid command
    response = client.delete(
        "/config/buckets/file",
        params={
            "file_path": MOCK_CONF_DIRPATH + "delete_this.conf"
        },
        json={"update_command": "invalid command"}
    )
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error"
    }

    rmtree(MOCK_CONF_DIRPATH)


def test_get_tar_archive() -> None:
    """Test for getting tar archive backup and verifying its contents"""
    make_mock_config_dir()

    response: Response = client.post(
        "/config/buckets/backup",
        json={"directory_path": MOCK_CONF_DIRPATH}
    )
    assert response.status_code == 200

    with open("tests/fakes/mock_conf.tar.gz", "wb") as bin_file:
        bin_file.write(response.content)
    backup_path = Path("tests/fakes/backup_conf")
    backup_path.mkdir(exist_ok=True)
    with tarfile.open("tests/fakes/mock_conf.tar.gz", "r|gz") as tar_file:
        tar_file.extractall(path=backup_path)
    _, mismatch, error = filecmp.cmpfiles(
        backup_path,
        MOCK_CONF_DIRPATH,
        ["mock.conf", "leave_this.conf"]
    )
    assert mismatch == []
    assert error == []

    os.remove("tests/fakes/mock_conf.tar.gz")
    rmtree(backup_path)
    rmtree(MOCK_CONF_DIRPATH)
