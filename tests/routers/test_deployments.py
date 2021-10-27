"""
Tests for routes at deployments endpoint
"""

import json
from shutil import rmtree
from typing import Any, Dict
from unittest.mock import patch

from fastapi.testclient import TestClient
from requests.models import Response

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import get_settings
from serverctl_deployd.main import app
from tests.fakes.fake_deployments import (MOCK_COMPOSE_FILE, MOCK_COMPOSE_PATH,
                                          MOCK_DB_CONFIG_CONTENT,
                                          MOCK_DB_JSON_PATH,
                                          MOCK_DEPLOYMENTS_PATH, MOCK_ENV_FILE,
                                          MOCK_ENV_PATH, TEST_DEPLOYMENT_PATH,
                                          UPDATED_DB_CONFIG_CONTENT,
                                          make_fake_deployment)

client = TestClient(app)


def settings_override() -> Settings:
    """Override settings with fake data file directory"""
    return Settings(deployments_dir="tests/fakes/.serverctl")


app.dependency_overrides[get_settings] = settings_override


def test_create_deployment() -> None:
    """Test for create deployment"""
    request_json = {
        "name": "test-deployment",
        "compose_file": MOCK_COMPOSE_FILE,
        "env_file": MOCK_ENV_FILE,
        "databases": MOCK_DB_CONFIG_CONTENT
    }

    # Successful request
    response: Response = client.post("/deployments/", json=request_json)
    assert response.status_code == 200
    assert response.json() == request_json

    with open(MOCK_COMPOSE_PATH, "r", encoding="utf-8") as compose_file:
        file_content = compose_file.read()
        assert file_content == MOCK_COMPOSE_FILE

    with open(MOCK_ENV_PATH, "r", encoding="utf-8") as env_file:
        env_content = env_file.read()
        assert env_content == MOCK_ENV_FILE

    with open(MOCK_DB_JSON_PATH, "r", encoding="utf-8") as json_file:
        env_content = json.load(json_file)
        assert env_content == request_json["databases"]

    # Deployment name already exists
    response = client.post("/deployments/", json=request_json)
    assert response.status_code == 409
    assert response.json() == {
        "detail": "A deployment with same name already exists"
    }

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_get_deployments() -> None:
    """Test for getting list of all deployments"""
    mock_deployment_list = {"sample1", "sample3", "sample2"}
    for deployment in mock_deployment_list:
        MOCK_DEPLOYMENTS_PATH.joinpath(deployment).mkdir(parents=True)

    # Successful request
    response: Response = client.get("/deployments/")
    assert response.status_code == 200
    assert set(response.json()) == mock_deployment_list

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_get_deployment() -> None:
    """Test for getting database config of a deployment"""
    make_fake_deployment()

    # Successful request
    response: Response = client.get("/deployments/test-deployment")
    assert response.status_code == 200
    assert response.json() == MOCK_DB_CONFIG_CONTENT

    # Deployment not found
    response = client.get("/deployments/non-existent-deployment")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment does not exist"
    }

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_update_deployment() -> None:
    """Test for updation of a deployment"""
    make_fake_deployment()

    request_json: Dict[str, Any] = {
        "compose_file": "fake compose file content",
        "env_file": "BAZ=baz",
        "databases": {
            "db2": {
                "username": "root"
            }
        }
    }

    # Successful request
    response: Response = client.patch(
        "/deployments/test-deployment",
        json=request_json
    )
    assert response.status_code == 204
    compose_file_content = MOCK_COMPOSE_PATH.read_text(encoding="utf-8")
    assert compose_file_content == request_json["compose_file"]
    env_file_content = MOCK_ENV_PATH.read_text(encoding="utf-8")
    assert env_file_content == request_json["env_file"]
    with open(MOCK_DB_JSON_PATH, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        assert json_data == UPDATED_DB_CONFIG_CONTENT

    # Deployment not found
    response = client.patch(
        "/deployments/non-existent-deployment",
        json=request_json
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment does not exist"
    }

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_delete_deployment() -> None:
    """Test for deletion of a deployment"""
    make_fake_deployment()

    # Successful request
    response: Response = client.delete("/deployments/test-deployment")
    assert response.status_code == 204
    assert not TEST_DEPLOYMENT_PATH.exists()

    # Deployment not found
    response = client.delete("/deployments/test-deployment")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment does not exist"
    }

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_compose_up() -> None:
    """Test for docker-compose down"""
    make_fake_deployment()

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response: Response = client.post("/deployments/test-deployment/up")
        assert response.status_code == 200
        assert response.json() == {"message": "docker-compose up executed"}

    # Deployment not found
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response = client.post("/deployments/non-existent-deployment/up")
        assert response.status_code == 404
        assert response.json() == {"detail": "Deployment does not exist"}

    # OSError
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.Popen",
        side_effect=OSError()
    ):
        response = client.post("/deployments/test-deployment/up")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

    rmtree(MOCK_DEPLOYMENTS_PATH)


def test_compose_down() -> None:
    """Test for docker-compose down"""
    make_fake_deployment()

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response: Response = client.post("/deployments/test-deployment/down")
        assert response.status_code == 200
        assert response.json() == {"message": "docker-compose down executed"}

    # Deployment not found
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response = client.post("/deployments/non-existent-deployment/down")
        assert response.status_code == 404
        assert response.json() == {"detail": "Deployment does not exist"}

    # OSError
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.Popen",
        side_effect=OSError()
    ):
        response = client.post("/deployments/test-deployment/down")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

    rmtree(MOCK_DEPLOYMENTS_PATH)
