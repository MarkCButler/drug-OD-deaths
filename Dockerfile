FROM node:16.17-bullseye-slim AS front-end-prod-env
# This stage installs dependencies needed for the front-end production build.

WORKDIR /app/front-end

ENV NODE_ENV=production

COPY ["front-end/package.json", "front-end/package-lock.json", "./"]

# Install front-end dependencies without devDependencies.  After the
# installation, clear the cache to reduce image size.
RUN npm clean-install --omit=dev && npm cache clean --force

CMD ["bash"]


FROM front-end-prod-env AS front-end-dev-env
# This stage installs front-end dev dependences on top of front-prod-env.
#
# In this development environment, the user gets a bash shell that can be used
# to execute commands defined in the scripts object of the file
# front-end/package.json.  The front-end and static directories located in the
# repo root on the host machine should be mounted into the container at
# directories /app/front-end and /app/static, respectively.   Commands from
# package.json executed in the container will then act on the source code from
# the host machine. For instance,
#   npm start
# will run the webpack development build with the --watch option using source
# code from the host machine as input. The output files from the webpack build
# will be placed in the static directory of the host machine.

ENV NODE_ENV=development

# Install devDependencies from package.json.  After the installation, clear the
# cache to reduce image size.
RUN npm install && npm cache clean --force


FROM front-end-prod-env AS front-end-prod-build
# This stage performs a production webpack build.  The output files are stored
# in the container directory /app/static.

# Copy files needed for the webpack build
COPY ["front-end/webpack*.js", "./"]
COPY ["front-end/src", "./src/"]

RUN ["npm", "run", "build"]


FROM python:3.10-slim-bullseye AS back-end-prod-env
# This stage first installs Poetry, a tool for Python dependency management.
# Poetry is then used to install the Python dependencies needed by the back end
# in production.  The dependencies are installed in a virtual environment, which
# will later be copied into the final stage of this buils.

# The next group of commands installs poetry using pipx.  The first command
# below minimizes image size by configuring pip not to create a cache.
RUN ["pip", "config", "set", "global.no-cache-dir", "true"]
RUN ["pip", "install", "pipx==1.2.0"]
# Update PATH to include the location at which pipx installs applications.
ENV PATH=${PATH}:/root/.local/bin
RUN ["pipx", "install", "poetry==1.2.2"]

# Configure poetry to install dependencies in a virtual environment named .venv
# located in the project root.  With default settings, poetry chooses a
# project-specific name for the virtual environment and stores it in a
# poetry-managed cache directory.  The setting modified by the RUN command below
# simplifies the task of finding the virtual environment and copying it into the
# final stage.
RUN ["poetry", "config", "virtualenvs.in-project", "true"]

WORKDIR /app

COPY ["pyproject.toml", "poetry.lock", "./"]

# Install dependencies, excluding the dev dependencies and the project itself.
RUN ["poetry", "install", "--no-root", "--without=dev"]

CMD ["bash"]


FROM back-end-prod-env AS back-end-dev-env
# This stage installs back-end dev dependences on top of back-prod-env.
#
# In this development environment, the user gets a bash shell that can be used
# to initialize the database or to run the app using flask's built-in server.
# The od_deaths, data, and static directories located in the repo root on the
# host machine should be mounted into the container at directories
# /app/od_deaths, /app/data, and /app/static, respectively.
#
# The command to initialize the database (located on the host machine) from
# within the container is
#   poetry run flask --app=od_deaths initialize-database
#
# In running flask's built-in server in debugging mode from within the
# container, the server settings should be customized.  By default, flask's
# built-in server only listens to 127.0.0.1 in debugging mode.  If the developer
# is using a browser running on the host to test the app, the request received
# by the app within the container will not come from 127.0.0.1.  One way to
# resolve this problem is to run the container with option
#   --publish 127.0.0.1:5000:5000
# and then start flask's built-in server using the command
#   poetry run flask --app=od_deaths --debug run --host=0.0.0.0
# With this configuration, the built-in server running in the container responds
# to all requests on port 5000, but on the host system, only requests from
# localhost are passed on to the container's network.
#
# Note that a separate container running front-end-dev-env is needed in order to
# run the webpack build (with output files placed in the static directory in the
# repo root on the host machine).

# Install the dev dependencies.
RUN ["poetry", "install", "--only=dev"]

EXPOSE 5000


FROM python:3.10-slim-bullseye AS production-build
# This stage does the following:
#   - Copy build artifacts from two previous stages: back-end-prod-env and
#     front-end-prod-build
#   - Copy the SQLite database from the host machine
#   - Copy the app's Python package from the host machine
#   - Create a non-privileged user to execute the app
#   - Start the app using gunicorn as a server.

WORKDIR /app

# Copy the Python virtual environment from back-end-prod-env
COPY --from=back-end-prod-env ["/app/.venv", "./.venv/"]

# Copy the output files from the webpack production build.
COPY --from=front-end-prod-build ["/app/static", "./static/"]

# Copy the SQLITE database, which should previously have been created and
# initialized on the host machine.  Note that database initialization can be
# done within a container running the build target back-end-dev-env as an image.
COPY ["data/*.sqlite", "./data/"]

# Copy the back-end source code.
COPY ["od_deaths", "./od_deaths/"]

RUN ["adduser", "--system", "--group", "app"]

USER app

# TODO: start the app using gunicorn

CMD ["bash"]
