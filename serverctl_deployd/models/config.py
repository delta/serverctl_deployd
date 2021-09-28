"""
Models for config buckets
"""

from typing import Optional, Set

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import DirectoryPath


class ListConfigBucket(BaseModel):
    """Class for obtaining list of files for a config bucket"""
    directory_path: DirectoryPath = Field(
        ..., title="Directory path for the bucket",
        description="This is the path of the directory\
            in which the config file(s) reside"
    )
    ignore_patterns: Optional[Set[str]] = Field(
        None, title="List of unix-shell style patterns for files to be ignored",
        description="Files which match this pattern will be ignored.\
            The expressions in this list should follow glob syntax"
    )


class ConfigBucket(BaseModel):
    """Class for validating config bucket creation and updation"""
    directory_path: DirectoryPath = Field(
        None, title="Directory path for the bucket",
        description="This is the path of the directory\
            in which the config file(s) reside"
    )
    ignore_patterns: Optional[Set[str]] = Field(
        None, title="List of unix-shell style patterns for files to be ignored",
        description="Files which match this pattern will be ignored.\
            The expressions in this list should follow glob syntax"
    )
    update_command: Optional[str] = Field(
        None, title="Command to be run to reload the config file(s)"
    )
