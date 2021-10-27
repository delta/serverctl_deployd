"""
A module for creating fake deployment for testing purposes
"""

import json
from pathlib import Path

MOCK_COMPOSE_FILE = """\
version '3.9'
services:
  mysql:
    image: mysql:8
    command: '--default-authentication-plugin=mysql_native_password'
    restart: always
    volumes:
      - ./mysql:/var/lib/mysql
    environment:
      - MYSQL_DATABASE=example
      - MYSQL_ROOT_PASSWORD=${PASSWORD}
  mongo:
    image: mongo:5.0.3
    restart: always
    volumes:
    - ./mongo:/data/db
  mongo-express:
    image: mongo-express
    restart: always
    ports:
      - 8081:8081
"""
MOCK_ENV_FILE = """\
PASSWORD=strongpw
FOO=foo
"""
MOCK_DB_CONFIG_CONTENT = {
    "db1": {
        "dbtype": "mysql",
        "username": "root",
        "password": "strongpw"
    },
    "db2": {
        "dbtype": "mongodb",
        "username": "user",
        "password": "strongerpw"
    }
}
MOCK_DEPLOYMENTS_PATH = Path("tests/fakes/.serverctl/")
TEST_DEPLOYMENT_PATH = MOCK_DEPLOYMENTS_PATH.joinpath("test-deployment")
MOCK_COMPOSE_PATH = TEST_DEPLOYMENT_PATH.joinpath("docker-compose.yml")
MOCK_ENV_PATH = TEST_DEPLOYMENT_PATH.joinpath(".env")
MOCK_DB_JSON_PATH = TEST_DEPLOYMENT_PATH.joinpath("databases.json")
UPDATED_DB_CONFIG_CONTENT = {
    "db1": {
        "dbtype": "mysql",
        "username": "root",
        "password": "strongpw"
    },
    "db2": {
        "dbtype": "mongodb",
        "username": "root",
        "password": "strongerpw"
    }
}


def make_fake_deployment() -> None:
    """Make a fake deployment for testing purposes"""
    TEST_DEPLOYMENT_PATH.mkdir(parents=True, exist_ok=True)
    MOCK_COMPOSE_PATH.write_text(MOCK_COMPOSE_FILE, encoding="utf-8")
    MOCK_ENV_PATH.write_text(MOCK_ENV_FILE, encoding="utf-8")

    with open(MOCK_DB_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(MOCK_DB_CONFIG_CONTENT, json_file, indent=4)
