"""
Fake responses for the Docker API
Adapted from https://github.com/docker/docker-py/blob/master/tests/unit/fake_api.py
"""

from typing import Any, Generator

FAKE_CONTAINER_ID = "3cc2351ab11b"
FAKE_LONG_ID = "e75ccd38cba33f61b09515e05f56fc243ef40186d600a9eeb6bc0bed8e2e1508"
FAKE_LOG_LINE_CONTENT = b"fake log"
FAKE_LOG_LINE_COUNT = 10
FAKE_IMAGE_ID = "sha256:e9aa60c60128"
FAKE_TAG = "sha256:e9aafierojv"
FAKE_CONTAINER_NAME = "jolly_black"
FAKE_LOGS_MESSAGE = 'Hello World\nThis is test logs'


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


def get_fake_inspect_container() -> tuple[int, dict[str, Any]]:
    """Get fake inspect data"""
    status_code = 200
    response = {
        "Id": FAKE_CONTAINER_ID,
        "Created": "2021-09-28T14:16:51.246200393Z",
        "Path": "/docker-entrypoint.sh",
        "Args": [
            "apache2-foreground"
        ],
        "State": {
            "Status": "running",
            "Running": True,
            "Paused": False,
            "Restarting": False,
            "OOMKilled": False,
            "Dead": False,
            "Pid": 85110,
            "ExitCode": 0,
            "Error": "",
            "StartedAt": "2021-09-28T14:16:51.540023895Z",
            "FinishedAt": "0001-01-01T00:00:00Z"
        },
        "Image": FAKE_IMAGE_ID,
        "Name": f"/{FAKE_CONTAINER_NAME}",
        "RestartCount": 0,
        "Driver": "overlay2",
        "Platform": "linux",
        "MountLabel": "",
        "ProcessLabel": "",
        "AppArmorProfile": "docker-default",
        "ExecIDs": None,
        "HostConfig": {
            "Binds": None,
            "ContainerIDFile": "",
            "LogConfig": {
                "Type": "json-file",
                "Config": {}
            },
            "NetworkMode": "default",
            "PortBindings": {
                "80/tcp": [
                    {
                        "HostIp": "",
                        "HostPort": "8088"
                    }
                ]
            },
            "RestartPolicy": {
                "Name": "no",
                "MaximumRetryCount": 0
            },
            "AutoRemove": False,
            "VolumeDriver": "",
            "VolumesFrom": None,
            "CapAdd": None,
            "CapDrop": None,
            "CgroupnsMode": "host",
            "Dns": [],
            "DnsOptions": [],
            "DnsSearch": [],
            "ExtraHosts": None,
            "GroupAdd": None,
            "IpcMode": "private",
            "Cgroup": "",
            "Links": None,
            "OomScoreAdj": 0,
            "PidMode": "",
            "Privileged": False,
            "PublishAllPorts": False,
            "ReadonlyRootfs": False,
            "SecurityOpt": None,
            "UTSMode": "",
            "UsernsMode": "",
            "ShmSize": 67108864,
            "Runtime": "runc",
            "ConsoleSize": [
                0,
                0
            ],
            "Isolation": "",
            "CpuShares": 0,
            "Memory": 0,
            "NanoCpus": 0,
            "CgroupParent": "",
            "BlkioWeight": 0,
            "BlkioWeightDevice": [],
            "BlkioDeviceReadBps": None,
            "BlkioDeviceWriteBps": None,
            "BlkioDeviceReadIOps": None,
            "BlkioDeviceWriteIOps": None,
            "CpuPeriod": 0,
            "CpuQuota": 0,
            "CpuRealtimePeriod": 0,
            "CpuRealtimeRuntime": 0,
            "CpusetCpus": "",
            "CpusetMems": "",
            "Devices": [],
            "DeviceCgroupRules": None,
            "DeviceRequests": None,
            "KernelMemory": 0,
            "KernelMemoryTCP": 0,
            "MemoryReservation": 0,
            "MemorySwap": 0,
            "MemorySwappiness": None,
            "OomKillDisable": False,
            "PidsLimit": None,
            "Ulimits": None,
            "CpuCount": 0,
            "CpuPercent": 0,
            "IOMaximumIOps": 0,
            "IOMaximumBandwidth": 0,
            "MaskedPaths": [
                "/proc/asound",
                "/proc/acpi",
                "/proc/kcore",
                "/proc/keys",
                "/proc/latency_stats",
                "/proc/timer_list",
                "/proc/timer_stats",
                "/proc/sched_debug",
                "/proc/scsi",
                "/sys/firmware"
            ],
            "ReadonlyPaths": [
                "/proc/bus",
                "/proc/fs",
                "/proc/irq",
                "/proc/sys",
                "/proc/sysrq-trigger"
            ]
        },
        "Mounts": [],
        "Config": {
            "Hostname": "03bfd76552c2",
            "Domainname": "",
            "User": "",
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            "ExposedPorts": {
                "80/tcp": {}
            },
            "Tty": True,
            "OpenStdin": True,
            "StdinOnce": True,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "PHP_INI_DIR=/usr/local/etc/php",
            ],
            "Cmd": [
                "apache2-foreground"
            ],
            "Image": "phpmyadmin:latest",
            "Volumes": None,
            "WorkingDir": "/var/www/html",
            "Entrypoint": [
                "/docker-entrypoint.sh"
            ],
            "OnBuild": None,
            "StopSignal": "SIGWINCH"
        },
        "NetworkSettings": {
            "Bridge": "",
            "SandboxID": "c5cec0eaeadea649b43ea0fb6cec5b60cb3c7b1b06813a1f07e6b7f4e2cb180e",
            "HairpinMode": False,
            "LinkLocalIPv6Address": "",
            "LinkLocalIPv6PrefixLen": 0,
            "Ports": {
                "80/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "8088"
                    },
                    {
                        "HostIp": "::",
                        "HostPort": "8088"
                    }
                ]
            },
            "SandboxKey": "/var/run/docker/netns/c5cec0eaeade",
            "SecondaryIPAddresses": None,
            "SecondaryIPv6Addresses": None,
            "EndpointID": "0ec86c835121720138dad365e7ad4c5520882801494a971932194f1dd3baee8b",
            "Gateway": "172.17.0.1",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "172.17.0.2",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "MacAddress": "02:42:ac:11:00:02",
            "Networks": {
                "bridge": {
                    "IPAMConfig": None,
                    "Links": None,
                    "Aliases": None,
                    "NetworkID": FAKE_LONG_ID,
                    "EndpointID": FAKE_LONG_ID,
                    "Gateway": "172.17.0.1",
                    "IPAddress": "172.17.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
                    "GlobalIPv6Address": "",
                    "GlobalIPv6PrefixLen": 0,
                    "MacAddress": "02:42:ac:11:00:02",
                    "DriverOpts": None
                }
            }
        }
    }

    return status_code, response


def get_fake_inspect_image() -> tuple[int, dict[str, Any]]:
    "Fake inspect image"
    status_code = 200
    response = {
        'Id': FAKE_IMAGE_ID,
        'Parent': "27cf784147099545",
        'Created': "2013-03-23T22:24:18.818426-07:00",
        'Container': FAKE_CONTAINER_ID,
        'Config': {'Labels': {'bar': 'foo'}},
        'ContainerConfig':
        {
            "Hostname": "",
            "User": "",
            "Memory": 0,
            "MemorySwap": 0,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "PortSpecs": "",
            "Tty": True,
            "OpenStdin": True,
            "StdinOnce": False,
            "Env": "",
            "Cmd": ["/bin/bash"],
            "Dns": "",
            "Image": "base",
            "Volumes": "",
            "VolumesFrom": "",
            "WorkingDir": ""
        },
        'Size': 6823592
    }
    return status_code, response


def get_fake_images() -> tuple[int, list[dict[str, Any]]]:
    "Fake list images"
    status_code = 200
    response = [{
        'Id': FAKE_IMAGE_ID,
        'Created': '2 days ago',
        'Repository': 'busybox',
        'RepoTags': ['busybox:latest', 'busybox:1.0'],
    }]
    return status_code, response


def get_fake_prune_containers() -> tuple[int, dict[str, Any]]:
    """Get fake prune containers response"""
    status_code = 200
    response = {
        "ContainersDeleted": [FAKE_LONG_ID],
        "SpaceReclaimed": 123
    }
    return status_code, response


def get_fake_prune_images() -> tuple[int, dict[str, Any]]:
    """Get fake prune images response"""
    status_code = 200
    response = {
        "ImagesDeleted": [FAKE_LONG_ID],
        "SpaceReclaimed": 123
    }
    return status_code, response


def get_fake_prune_volumes() -> tuple[int, dict[str, Any]]:
    """Get fake prune volumes response"""
    status_code = 200
    response = {
        "VolumesDeleted": [FAKE_LONG_ID],
        "SpaceReclaimed": 123
    }
    return status_code, response


def get_fake_prune_networks() -> tuple[int, dict[str, Any]]:
    """Get fake prune networks response"""
    status_code = 200
    response = {
        "NetworksDeleted": [FAKE_LONG_ID]
    }
    return status_code, response


def get_fake_prune_builds() -> tuple[int, dict[str, Any]]:
    """Get fake prune build caches response"""
    status_code = 200
    response = {
        "CachesDeleted": [FAKE_LONG_ID],
        "SpaceReclaimed": 123
    }
    return status_code, response


def _get_log_stream() -> Generator[bytes, None, None]:
    for _ in range(FAKE_LOG_LINE_COUNT):
        yield FAKE_LOG_LINE_CONTENT


def get_fake_logs() -> tuple[int, Generator[bytes, None, None]]:
    """Get fake container logs"""
    status_code = 200
    return status_code, _get_log_stream()


def get_fake_logs_response() -> tuple[int, bytes]:
    """Get fake logs response"""
    status_code = 200
    response = (bytes(FAKE_LOGS_MESSAGE, 'ascii'))
    return status_code, response
