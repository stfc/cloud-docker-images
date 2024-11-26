ARG HUGGING_FACE_TOKEN="NOTSET"

USER root
RUN apt-get update && apt-get upgrade -y && \
    apt-get install npm -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/ollama /opt/models && \
    chown -R ${NB_UID} /opt/ollama /opt/models && \
    chmod -R +rwX /opt/ollama /opt/models
    
ENV OLLAMA_DIR="/opt/ollama"
ENV OLLAMA_RELEASE_URL="https://github.com/ollama/ollama/releases/download/v0.4.2/ollama-linux-amd64.tgz"
RUN echo -e "\nInstalling Ollama...\n" && \
    wget --quiet -O- "$OLLAMA_RELEASE_URL" | tar -xz -C "$OLLAMA_DIR"

COPY install-sciml-deps.sh /usr/local/bin/

RUN chown ${NB_UID} /usr/local/bin/install-sciml-deps.sh
RUN chmod +rx /usr/local/bin/install-sciml-deps.sh

USER $NB_UID
RUN /usr/local/bin/install-sciml-deps.sh \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

ENV HF_HOME=/opt/models

RUN echo -e "\nDownloading spacy model...\n" && \
    python -m spacy download en_core_web_sm

ENV HF_HUB_ENABLE_HF_TRANSFER=1
RUN pip install huggingface_hub[hf_transfer] && \
    huggingface-cli login --token ${HUGGING_FACE_TOKEN}

# Split model download up into individual layer to avoid Harbor choking on >32GB layers
RUN huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct model-00001-of-00004.safetensors
RUN huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct model-00002-of-00004.safetensors
RUN huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct model-00003-of-00004.safetensors
RUN huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct model-00004-of-00004.safetensors
RUN huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct

USER ${NB_UID}
