FROM quay.io/jupyter/pytorch-notebook:cuda12-python-3.11

USER root
RUN apt-get update && apt-get upgrade -y && \
    apt-get install npm -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/ollama /opt/models && \
    chown -R ${NB_UID} /opt/ollama /opt/models && \
    chmod -R +rwX /opt/ollama /opt/models

COPY install-sciml-deps.sh /usr/local/bin/
COPY download-models.py /usr/local/bin/

RUN chown ${NB_UID} /usr/local/bin/install-sciml-deps.sh /usr/local/bin/download-models.py
RUN chmod +rx /usr/local/bin/install-sciml-deps.sh /usr/local/bin/download-models.py

USER $NB_UID
RUN /usr/local/bin/install-sciml-deps.sh \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

RUN echo -e "\nInstalling Ollama...\n" && \
    OLLAMA_DIR="/opt/ollama" \
    OLLAMA_RELEASE_URL="https://github.com/ollama/ollama/releases/download/v0.4.2/ollama-linux-amd64.tgz" \
    wget --quiet -O- "$OLLAMA_RELEASE_URL" | tar -xz -C "$OLLAMA_DIR"

ENV HF_HOME=/opt/models
# https://huggingface.co/docs/datasets/en/cache
RUN /usr/local/bin/download-models.py \
&& fix-permissions "${CONDA_DIR}" \
&& fix-permissions "/home/${NB_USER}"

USER ${NB_UID}
