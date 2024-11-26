#!/bin/bash

echo -e "\nUninstalling conflicting libraries...\n"
pip uninstall -y tensorflow

echo -e "\nInstalling essential Python libraries...\n"
pip install --no-cache-dir --upgrade flask gdown jupyter matplotlib numpy pandas scipy spacy tqdm

echo -e "\nInstalling HuggingFace libraries...\n"
pip install --no-cache-dir --upgrade huggingface_hub transformers accelerate

echo -e "\nInstalling bitsandbytes...\n"
pip install --no-cache-dir bitsandbytes -U

echo -e "\nInstalling LLM libraries...\n"
pip install --no-cache-dir --upgrade faiss-cpu networkx langchain langchain_community langgraph vllm

echo -e "\nInstalling Localtunnel...\n"
npm install -g localtunnel
