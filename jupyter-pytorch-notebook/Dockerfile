FROM cschranz/gpu-jupyter:v1.7_cuda-12.2_ubuntu-22.04_python-only

USER root
# The base image only gets updated when a new version of CUDA is released.
# We need to update the base image to get the latest security updates.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID
RUN set -ex \
 && buildDeps=' \
    transformers \
    accelerate \
    bitsandbytes \
 ' \
 && pip install --no-cache-dir $buildDeps \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

#switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}

