FROM ubuntu:24.04

ARG CIRCT_VERSION=1.147.0

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    git \
    iverilog \
    less \
    nano \
    ninja-build \
    python3 \
    python3-venv \
    ripgrep \
    vim \
    wget \
    z3 \
    libedit2 \
    libffi8 \
    libtinfo6 \
    libxml2-dev \
    libz3-dev \
    libzstd1 \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt && \
    wget -qO /tmp/circt.tar.gz \
      "https://github.com/llvm/circt/releases/download/firtool-${CIRCT_VERSION}/circt-full-shared-linux-x64.tar.gz" && \
    tar -xzf /tmp/circt.tar.gz -C /opt && \
    mv "/opt/firtool-${CIRCT_VERSION}" /opt/circt && \
    rm /tmp/circt.tar.gz

COPY requirements.txt /tmp/tutorial-requirements.txt

RUN python3 -m venv /opt/mlir-python && \
    /opt/mlir-python/bin/pip install --no-cache-dir \
      -r /tmp/tutorial-requirements.txt && \
    rm /tmp/tutorial-requirements.txt

ENV VIRTUAL_ENV="/opt/mlir-python"
ENV PATH="/opt/mlir-python/bin:/opt/circt/bin:/workspace/build/bin:${PATH}"
ENV CMAKE_PREFIX_PATH="/opt/circt"
ENV LD_LIBRARY_PATH="/opt/circt/lib"
ENV CC=gcc
ENV CXX=g++

WORKDIR /workspace
COPY . /workspace

RUN ./scripts/build.sh && \
    install -m 0755 build/bin/circt-tutorial-opt \
      /usr/local/bin/circt-tutorial-opt

CMD ["/bin/bash"]
