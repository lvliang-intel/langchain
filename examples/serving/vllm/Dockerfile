FROM vault.habana.ai/gaudi-docker/1.14.0/ubuntu22.04/habanalabs/pytorch-installer-2.1.1:latest as hpu

ENV LANG=en_US.UTF-8
ENV PYTHONPATH=/root:/usr/lib/habanalabs/
ARG REPO=https://github.com/HabanaAI/vllm-fork.git
ARG BRANCH=habana_main

RUN apt-get update && \
    apt-get install git-lfs && \
    git-lfs install


# Download gaudi-vllm code
#SHELL ["/bin/bash", "--login", "-c"]
RUN git clone --single-branch --branch=${BRANCH} ${REPO}
WORKDIR /vllm-fork

# Build gaudi-vllm
RUN cd /vllm-fork && \
    pip install -r requirements-hpu.txt && \
    python setup.py install

# Install langchain
RUN pip install langchain langchain_community -q