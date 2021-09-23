"""
Models for general exception responses
"""

from pydantic import BaseModel


class GenericError(BaseModel):
    """Model for generic error with detail"""
    detail: str
