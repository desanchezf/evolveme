# This Dockerfile is used to deploy a simple single-container Reflex app instance.
FROM python:3.11

ARG uv=/root/.cargo/bin/uv

# Install `uv` for faster package bootstrapping
ENV VIRTUAL_ENV=/usr/local
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Check if uv was installed correctly
RUN ls -l /root/.cargo/bin/ && /root/.cargo/bin/uv --version

# Copy local context to `/app` inside container (see .dockerignore)
WORKDIR /app
COPY . .

# Install app requirements and reflex in the container
# First try using uv, if it fails, use pip directly
RUN if ! $uv pip install -r requirements.txt; then pip install -r requirements.txt; fi

# Deploy templates and prepare app
RUN reflex init

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

# Always apply migrations before starting the backend.
CMD reflex db migrate && reflex run --env prod
