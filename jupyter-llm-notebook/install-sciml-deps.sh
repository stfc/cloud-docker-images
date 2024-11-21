#!/bin/bash

echo -e "\nUninstalling conflicting libraries...\n"
pip uninstall -y tensorflow

echo -e "\nInstalling essential Python libraries...\n"
pip install --no-cache-dir --upgrade flask gdown jupyter matplotlib numpy pandas scipy spacy tqdm

echo -e "\nInstalling PyTorch...\n"
pip install --no-cache-dir --upgrade torch torchvision torchaudio

echo -e "\nInstalling HuggingFace libraries...\n"
pip install --no-cache-dir --upgrade huggingface_hub transformers accelerate

echo -e "\nInstalling bitsandbytes...\n"
pip install --no-cache-dir bitsandbytes -U

echo -e "\nInstalling LLM libraries...\n"
pip install --no-cache-dir --upgrade faiss-cpu networkx langchain langchain_community langgraph vllm

echo -e "\nDownloading spaCy language model...\n"
python -m spacy download en_core_web_sm

echo -e "\nInstalling Localtunnel...\n"
npm install -g localtunnel

echo -e "\nInstalling Ollama...\n"
OLLAMA_DIR="/opt/ollama"
OLLAMA_RELEASE_URL="https://github.com/ollama/ollama/releases/download/v0.4.2/ollama-linux-amd64.tgz"
wget --quiet -O- "$OLLAMA_RELEASE_URL" | tar -xz -C "$OLLAMA_DIR"
