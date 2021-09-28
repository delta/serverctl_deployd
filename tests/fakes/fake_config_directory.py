"""
A module to create a mock config file directory for testing purposes
"""

from pathlib import Path

MOCK_CONF_DIRPATH = "tests/fakes/mock_confs/"
MOCK_CONF_FILEPATH = MOCK_CONF_DIRPATH + "mock.conf"
MOCK_CONF_FILE_CONTENT = "FakeSetting   fake-value"
MOCK_CONF_NEW_CONTENT = "FakeSetting   updated-fake-value"
MOCK_FILE_HASH = "d91a2831aff3a24753083d87786d7f8e8703f9f4612e15ae6f7939c37a2df954"


def make_mock_config_dir() -> None:
    """Make a mock config file directory and add mock conf files"""
    Path(MOCK_CONF_DIRPATH).mkdir(exist_ok=True)
    with open(
        MOCK_CONF_FILEPATH,
        'w', encoding='utf8'
    ) as conf_file:
        conf_file.write(MOCK_CONF_FILE_CONTENT)
    with open(
        MOCK_CONF_DIRPATH + 'leave_this.conf',
        'w', encoding='utf8'
    ) as conf_file:
        conf_file.write(MOCK_CONF_FILE_CONTENT)
