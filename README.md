<h1 align="center">serverctl Deployment Daemon</h1>
<p align="center">
  <a href="https://github.com/delta/serverctl_deployd/actions/workflows/lint.yml">
      <img src="https://github.com/delta/serverctl_deployd/actions/workflows/lint.yml/badge.svg?branch=main"/>
  </a>
  <a href="https://github.com/delta/serverctl_deployd/actions/workflows/ci.yml">
      <img src="https://github.com/delta/serverctl_deployd/actions/workflows/ci.yml/badge.svg"/>
  </a>
  <a href="https://github.com/delta/serverctl_deployd/actions/workflows/docs.yml">
      <img src="https://github.com/delta/serverctl_deployd/actions/workflows/docs.yml/badge.svg"/>
  </a>
  <a href="https://codecov.io/gh/delta/serverctl_deployd">
      <img src="https://codecov.io/gh/delta/serverctl_deployd/branch/main/graph/badge.svg?token=LxVYcZoZJ6"/>
  </a>
</p>

## Local development

1. Clone the repo
2. Run `cp .env.example .env`
3. Run `virtualenv --clear venv`
4. Run `source ./venv/bin/activate`
5. Run `pip install -r requirements-dev.txt`
6. Run `pre-commit install` to install the git hooks for linting and testing
7. Run `uvicorn serverctl_deployd.main:app --reload` to start the server

## License

MIT License

Copyright (c) 2021 Delta Force
