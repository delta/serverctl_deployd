"""
Fake responses for the Docker API

Adapted from https://github.com/docker/docker-py/blob/master/tests/unit/fake_api.py
"""

from typing import Any, Generator

FAKE_CONTAINER_ID = "3cc2351ab11b"
FAKE_LOG_LINE_CONTENT = b"fake log"
FAKE_LOG_LINE_COUNT = 10


def get_fake_containers() -> tuple[int, list[dict[str, str]]]:
    """Get list of fake containers"""
    status_code = 200
    response = [{
        "Id": FAKE_CONTAINER_ID,
        "Image": "busybox:latest",
        "Created": "2 days ago",
        "Command": "true",
        "Status": "fake status"
    }]
    return status_code, response


def get_fake_inspect_container(tty: bool = False) -> tuple[int, dict[str, Any]]:
    """Get fake inspect data"""
    status_code = 200
    response = {
        "Id": FAKE_CONTAINER_ID,
        "Config": {"Labels": {"foo": "bar"}, "Privileged": True, "Tty": tty},
        "ID": FAKE_CONTAINER_ID,
        "Image": "busybox:latest",
        "Name": "foobar",
        "State": {
            "Status": "running",
            "Running": True,
            "Pid": 0,
            "ExitCode": 0,
            "StartedAt": "2013-09-25T14:01:18.869545111+02:00",
            "Ghost": False
        },
        "HostConfig": {
            "LogConfig": {
                "Type": "json-file",
                "Config": {}
            },
        },
        "MacAddress": "02:42:ac:11:00:0a"
    }
    return status_code, response


def _get_log_stream() -> Generator[bytes, None, None]:
    for _ in range(FAKE_LOG_LINE_COUNT):
        yield FAKE_LOG_LINE_CONTENT


def get_fake_logs() -> tuple[int, Generator[bytes, None, None]]:
    """Get fake container logs"""
    status_code = 200
    return status_code, _get_log_stream()
