"""
Models related to the deployments feature
"""

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel
from pydantic.fields import Field


class DBType(str, Enum):
    """Enum of supported databases"""
    MYSQL = "mysql"
    MONGODB = "mongodb"


class DBConfig(BaseModel):
    """Class for database config"""
    dbtype: DBType = Field(
        ..., title="Type of the database service"
    )
    username: str = Field(
        ..., title="Username for connecting to database service"
    )
    password: str = Field(
        ..., title="Password for connecting to the database service"
    )


class UpdateDBConfig(BaseModel):
    """Class for updating database config"""
    dbtype: Optional[DBType] = Field(
        None, title="Type of the database service"
    )
    username: Optional[str] = Field(
        None, title="Username for connecting to database service"
    )
    password: Optional[str] = Field(
        None, title="Password for connecting to the database service"
    )


class Deployment(BaseModel):
    """Class for deployment"""
    compose_path: str = Field(
        ..., title="Path of the docker-compose file"
    )
    databases: Optional[Dict[str, DBConfig]] = Field(
        None, title="List of database services"
    )


class NamedDeployment(Deployment):
    """Class for deployment with name input"""
    name: str = Field(
        ..., title="Name of the deployment"
    )


class UpdateDeployment(BaseModel):
    """Class for updating deployment"""
    compose_path: Optional[str] = Field(
        None, title="Path of the docker-compose file"
    )
    databases: Optional[Dict[str, UpdateDBConfig]] = Field(
        None, title="List of database services"
    )
