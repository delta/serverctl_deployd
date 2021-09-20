"""
Contains the global configuration for the API.
(Modify the .env file to change the values)
"""

import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings

load_dotenv(find_dotenv())


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Class for global settings"""
    environment: Optional[str] = os.getenv("ENVIRONMENT")
    log_level: str = os.getenv("LOGLEVEL", "WARNING").upper()


settings = Settings()
