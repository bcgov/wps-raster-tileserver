# When building in openshift, you can reference the image in openshift:
# FROM image-registry.openshift-image-registry.svc:5000/e1e498-tools/uvicorn-gunicorn-fastapi:python3.9
#
# When building local, you can reference the docker image.
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ARG USERNAME=worker
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get update --fix-missing && apt-get -y install libgdal-dev

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN chown worker /app
USER worker
ENV PATH="/home/worker/.local/bin:${PATH}"

# Update pip.
RUN python -m pip install --upgrade pip

# Install dependencies.
WORKDIR /app
# Tried to use ADD, but it fails due to e-tag error - so keep using curl.
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy poetry files.
COPY --chown=worker:worker poetry.lock pyproject.toml ./
RUN poetry install --no-dev
# We have to install gdal manually. The version differs from platform to platform.
RUN poetry run python -m pip install pygdal==3.2.2.10

# Copy the app.
COPY --chown=worker:worker ./cogtiler ./cogtiler

EXPOSE 7800
