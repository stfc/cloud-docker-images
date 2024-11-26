#!/bin/bash

set -eux -o pipefail

# Skip installing torch audio and vision
# as they're installed here https://github.com/jupyter/docker-stacks/blob/main/images/pytorch-notebook/cuda12/Dockerfile#L16

echo -e "\nInstalling all pip libraries...\n"
pip install --no-cache-dir --upgrade \
    flask gdown jupyter matplotlib numpy pandas scipy spacy tqdm \
    huggingface_hub transformers accelerate datasets \
    bitsandbytes \
    faiss-cpu networkx langchain langchain_community langgraph vllm \
    spacy download

echo -e "\nDownloading spacy model...\n"
python -m spacy download en_core_web_sm

echo -e "\nInstalling Localtunnel...\n"
npm install -g localtunnel
