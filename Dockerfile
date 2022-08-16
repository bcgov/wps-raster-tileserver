# As per
# https://github.com/tiangolo/uvicorn-gunicorn-docker#-warning-you-probably-dont-need-this-docker-image
# we build a docker image from scratch
FROM python:3.10-bullseye

ARG USERNAME=worker
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get update --fix-missing && apt-get -y install libgdal-dev

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN mkdir /app
RUN chown worker /app
USER worker
ENV PATH="/home/worker/.local/bin:${PATH}"

# RUN mkdir /home/worker/.cache/pypoetry
# RUN chown worker /home/worker/.cache/pypoetry
ENV POETRY_CACHE_DIR="/home/worker/.cache/pypoetry"

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

# Openshift runs with a random non-root user, so switching our user to 1001 allows us
# to test locally with similar conditions to what we may find in openshift.
USER 1001

EXPOSE 7800
# https://www.uvicorn.org/deployment/#gunicorn
# We need to configure openshift to handle load. Using anything more than 1 worker, doesn't really result in any performance
# increase in openshift. We need to run serverless or autoscale or something.
CMD ["poetry", "run", "gunicorn", "cogtiler.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:7800"]