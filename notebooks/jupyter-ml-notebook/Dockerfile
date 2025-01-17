FROM cschranz/gpu-jupyter:v1.8_cuda-12.5_ubuntu-22.04_python-only

# Switch to root to install packages
USER root

# The base image only gets updated when a new version of CUDA is released.
# We need to update the base image to get the latest security updates.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}