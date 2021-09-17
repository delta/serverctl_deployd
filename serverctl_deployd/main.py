"""
Entrypoint for the API.
"""

import json
import sys

import uvicorn
from fastapi import Depends, FastAPI

from serverctl_deployd.config import Settings
from serverctl_deployd.dependencies import check_authentication
from serverctl_deployd.routers import config, deployments, docker

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
