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
    name: str = Field(
        ..., title="Name of the deployment"
    )
    compose_file: str = Field(
        ..., title="Content of the docker-compose file"
    )
    env_file: Optional[str] = Field(
        None, title="Content of the .env file"
    )
    databases: Optional[Dict[str, DBConfig]] = Field(
        None, title="List of database services"
    )


class UpdateDeployment(BaseModel):
    """Class for updating deployment"""
    compose_file: str = Field(
        None, title="Content of the docker-compose file"
    )
    env_file: Optional[str] = Field(
        None, title="Content of the .env file"
    )
    databases: Optional[Dict[str, UpdateDBConfig]] = Field(
        None, title="List of database services"
    )
