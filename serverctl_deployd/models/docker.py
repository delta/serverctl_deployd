"""
Models for Docker API requests and responses
"""

from typing import Optional

from pydantic import BaseModel, Field


class PruneRequest(BaseModel):
    """Model for prune request"""
    containers: Optional[bool] = Field(
        False, description="Delete stopped containers")
    images: Optional[bool] = Field(False, description="Delete unused images")
    volumes: Optional[bool] = Field(False, description="Delete unused volumes")
    networks: Optional[bool] = Field(
        False, description="Delete unused networks")
    build_cache: Optional[bool] = Field(
        False, description="Delete the builder cache")
    all: Optional[bool] = Field(
        False, description="Delete stopped containers, unused images, unused volumes,\
            unused networks and the builder cache")


class ContainersDeleted(BaseModel):
    """Model for pruned containers in prune response"""
    containers_deleted: list[str] = Field(
        None, alias="ContainersDeleted", description="Containers deleted")
    space_reclaimed: int = Field(
        None, alias="SpaceReclaimed", description="Space reclaimed")


class ImagesDeleted(BaseModel):
    """Model for pruned images in prune response"""
    images_deleted: list[str] = Field(
        None, alias="ImagesDeleted", description="Images deleted")
    space_reclaimed: int = Field(
        None, alias="SpaceReclaimed", description="Space reclaimed")


class NetworksDeleted(BaseModel):
    """Model for pruned networks in prune response"""
    networks_deleted: list[str] = Field(
        None, alias="NetworksDeleted", description="Networks deleted")


class VolumesDeleted(BaseModel):
    """Model for pruned volumes in prune response"""
    volumes_deleted: list[str] = Field(
        None, alias="VolumesDeleted", description="Volumes deleted")


class BuildCachesDeleted(BaseModel):
    """Model for pruned build caches in prune response"""
    caches_deleted: list[str] = Field(
        None, alias="CachesDeleted", description="Caches deleted")
    space_reclaimed: int = Field(
        None, alias="SpaceReclaimed", description="Space reclaimed")


class PruneResponse(BaseModel):
    """Model for prune response"""
    containers: Optional[ContainersDeleted] = None
    images: Optional[ImagesDeleted] = None
    networks: Optional[NetworksDeleted] = None
    volumes: Optional[VolumesDeleted] = None
    build_cache: Optional[BuildCachesDeleted] = None
