FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    nodejs \
    npm \
    net-tools \
    iputils-ping \
    arp-scan \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create python3 symlink
RUN ln -sf /usr/bin/python3.12 /usr/bin/python3 \
    && ln -sf /usr/bin/python3 /usr/bin/python

# Set up non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# The base image already has vscode user, just ensure proper permissions
RUN if [ "$USER_GID" != "1000" ] || [ "$USER_UID" != "1000" ]; then \
    groupmod --gid $USER_GID $USERNAME \
    && usermod --uid $USER_UID --gid $USER_GID $USERNAME \
    && chown -R $USER_UID:$USER_GID /home/$USERNAME; \
    fi

# Allow vscode user to use network tools
RUN setcap cap_net_raw,cap_net_admin+eip /usr/sbin/arp-scan || true

USER $USERNAME

# Set working directory
WORKDIR /workspace
