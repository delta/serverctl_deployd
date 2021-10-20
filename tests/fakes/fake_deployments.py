"""
A module for creating fake deployment for testing purposes
"""

import json

MOCK_COMPOSE_FILE = "tests/fakes/docker-compose.yml"
MOCK_DEPLOYMENTS_FILE = "tests/fakes/deployments.json"
DEPLOYMENTS_DATA_CONTENT = {
    "sample-deployment": {
        "compose_path": MOCK_COMPOSE_FILE,
        "databases": {
            "sample-db": {
                "dbtype": "mysql",
                "username": "root",
                "password": "strongpw"
            }
        }
    }
}
UPDATED_DATA_CONTENT = {
    "compose_path": MOCK_COMPOSE_FILE,
    "databases": {
        "sample-db": {
            "dbtype": "mongodb",
            "username": "root",
            "password": "strongpw"
        }
    }
}


def make_fake_deployments_file() -> None:
    """Make a fake deployments JSON file"""
    with open(MOCK_DEPLOYMENTS_FILE, "w", encoding="utf-8") as json_file:
        json.dump(DEPLOYMENTS_DATA_CONTENT, json_file, indent=4)
