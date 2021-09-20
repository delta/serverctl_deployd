"""
Entrypoint for the API.
"""

import json
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import check_authentication
from serverctl_deployd.routers import config, deployments, docker

load_dotenv(dotenv_path=".env")

rotating_file_handler = TimedRotatingFileHandler("serverctl_deployd.log",
                                                 when="W0",
                                                 backupCount=48,
                                                 utc=True)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING").upper(),
                    format="%(asctime)s %(levelname)s: %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout), rotating_file_handler])

settings = Settings()
app: FastAPI = FastAPI(dependencies=[Depends(check_authentication)])


app.include_router(config.router)
app.include_router(deployments.router)
app.include_router(docker.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Basic route for testing"""
    return {"message": "Working!"}


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "docs":
        print(json.dumps(app.openapi(), indent=4))
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
