FROM cschranz/gpu-jupyter:v1.7_cuda-12.2_ubuntu-22.04_python-only

USER root
# The base image only gets updated when a new version of CUDA is released.
# We need to update the base image to get the latest security updates.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
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

# https://huggingface.co/docs/datasets/en/cache
ENV HF_HOME=/opt/models
RUN /usr/local/bin/download-models.py \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

#switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
