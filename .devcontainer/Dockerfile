FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends make git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
