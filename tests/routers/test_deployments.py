"""
Tests for routes at deployments endpoint
"""

import json
import os
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

from fastapi.testclient import TestClient
from requests.models import Response

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import get_settings
from serverctl_deployd.main import app
from tests.fakes.fake_deployments import (DEPLOYMENTS_DATA_CONTENT,
                                          MOCK_COMPOSE_FILE,
                                          MOCK_DEPLOYMENTS_FILE,
                                          UPDATED_DATA_CONTENT,
                                          make_fake_deployments_file)

client = TestClient(app)


def settings_override() -> Settings:
    """Override settings with fake data file directory"""
    return Settings(data_files_dir="tests/fakes/")


app.dependency_overrides[get_settings] = settings_override


def test_create_deployment() -> None:
    """Test for create deployment"""
    make_fake_deployments_file()
    Path(MOCK_COMPOSE_FILE).touch()
    request_json = {
        "name": "test-deployment",
        "compose_path": MOCK_COMPOSE_FILE,
        "databases": {
            "db1": {
                "dbtype": "mysql",
                "username": "root",
                "password": "strongpw"
            },
            "db2": {
                "dbtype": "mongodb",
                "username": "superuser",
                "password": "strongerpw"
            }
        }
    }

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.run"):
        response: Response = client.post(
            "/deployments/",
            json=request_json
        )
        assert response.status_code == 200
        assert response.json() == request_json
    with open(MOCK_DEPLOYMENTS_FILE, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        deployment_in_file = json_data[request_json["name"]]
        deployment_details = request_json
        del deployment_details["name"]
        assert deployment_in_file == deployment_details

    # Invalid compose file
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.run",
        side_effect=CalledProcessError(1, "")
    ):
        request_json["name"] = "has-invalid-compose-file"
        response = client.post(
            "/deployments/",
            json=request_json
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Invalid docker-compose file"
        }

    # Deployment name already exists
    with patch("serverctl_deployd.routers.deployments.subprocess.run"):
        request_json["name"] = "test-deployment"
        response = client.post(
            "/deployments/",
            json=request_json
        )
        assert response.status_code == 409
        assert response.json() == {
            "detail": "A deployment with same name already exists"
        }

    os.remove(MOCK_COMPOSE_FILE)
    os.remove(MOCK_DEPLOYMENTS_FILE)


def test_get_deployments() -> None:
    """Test for getting details of all deployments"""
    make_fake_deployments_file()

    # Successful request
    response: Response = client.get("/deployments/")
    assert response.status_code == 200
    assert response.json() == DEPLOYMENTS_DATA_CONTENT

    # Deployments file does not exist
    os.remove(MOCK_DEPLOYMENTS_FILE)
    response = client.get("/deployments/")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployments data does not exist"
    }


def test_get_deployment() -> None:
    """Test for getting details of a deployment"""
    make_fake_deployments_file()

    # Successful request
    response: Response = client.get("/deployments/sample-deployment")
    assert response.status_code == 200
    assert response.json() == DEPLOYMENTS_DATA_CONTENT["sample-deployment"]

    # Deployment not found
    response = client.get("/deployments/non-existent-deployment")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment does not exist"
    }

    os.remove(MOCK_DEPLOYMENTS_FILE)


def test_update_deployment() -> None:
    """Test for updation of a deployment"""
    make_fake_deployments_file()
    request_json = {
        "compose_path": MOCK_COMPOSE_FILE,
        "databases": {
            "sample-db": {
                "dbtype": "mongodb",
            }
        }
    }

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.run"):
        response: Response = client.patch(
            "/deployments/sample-deployment",
            json=request_json
        )
        assert response.status_code == 200
        assert response.json() == UPDATED_DATA_CONTENT
        with open(MOCK_DEPLOYMENTS_FILE, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            deployment_in_file = json_data["sample-deployment"]
            assert deployment_in_file == UPDATED_DATA_CONTENT

    # Invalid compose file
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.run",
        side_effect=CalledProcessError(1, "")
    ):
        response = client.patch(
            "/deployments/sample-deployment",
            json=request_json
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": "Invalid docker-compose file"
        }

    # Deployment not found
    with patch("serverctl_deployd.routers.deployments.subprocess.run"):
        response = client.patch(
            "/deployments/non-existent-deployment",
            json=request_json
        )
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Deployment does not exist"
        }

    os.remove(MOCK_DEPLOYMENTS_FILE)


def test_delete_deployment() -> None:
    """Test for deletion of a deployment"""
    make_fake_deployments_file()

    # Successful request
    response: Response = client.delete("/deployments/sample-deployment")
    assert response.status_code == 204
    with open(MOCK_DEPLOYMENTS_FILE, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        assert "sample-deployment" not in json_data

    # Deployment not found
    response = client.delete("/deployments/sample-deployment")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment does not exist"
    }

    os.remove(MOCK_DEPLOYMENTS_FILE)


def test_compose_up() -> None:
    """Test for docker-compose down"""
    make_fake_deployments_file()

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response: Response = client.post("/deployments/sample-deployment/up")
        assert response.status_code == 200
        assert response.json() == {"message": "docker-compose up executed"}

    # OSError
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.Popen",
        side_effect=OSError()
    ):
        response = client.post("/deployments/sample-deployment/up")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

    os.remove(MOCK_DEPLOYMENTS_FILE)


def test_compose_down() -> None:
    """Test for docker-compose down"""
    make_fake_deployments_file()

    # Successful request
    with patch("serverctl_deployd.routers.deployments.subprocess.Popen"):
        response: Response = client.post("/deployments/sample-deployment/down")
        assert response.status_code == 200
        assert response.json() == {"message": "docker-compose down executed"}

    # OSError
    with patch(
        "serverctl_deployd.routers.deployments.subprocess.Popen",
        side_effect=OSError()
    ):
        response = client.post("/deployments/sample-deployment/down")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

    os.remove(MOCK_DEPLOYMENTS_FILE)
