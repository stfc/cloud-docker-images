FROM cschranz/gpu-jupyter:v1.7_cuda-12.2_ubuntu-22.04_python-only

USER root
# The base image only gets updated when a new version of CUDA is released.
# We need to update the base image to get the latest security updates.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY install-sciml-deps.sh /home/${NB_USER}
RUN chown ${NB_UID} /home/${NB_USER}/install-sciml-deps.sh
RUN chmod +rx /home/${NB_USER}/install-sciml-deps.sh

USER $NB_UID
RUN /home/${NB_USER}/install-sciml-deps.sh \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

#switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}