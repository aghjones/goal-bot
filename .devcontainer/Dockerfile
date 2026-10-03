FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

# The base image ships a Yarn apt source whose signing key has expired, which
# makes `apt-get update` fail. We don't need Yarn, so drop the source.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libmediainfo0v5 curl make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
