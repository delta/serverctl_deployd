"""
Contains the global configuration for the API.
(Modify the .env file to change the values)
"""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv(dotenv_path="../.env")


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Class for global settings"""

    environment: Optional[str] = os.getenv("ENVIRONMENT")


settings = Settings()
