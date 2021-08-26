FROM jupyter/tensorflow-notebook
# Get the latest image tag at:
# https://hub.docker.com/r/jupyter/minimal-notebook/tags/
# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/minimal-notebook/Dockerfile

# Switch to root to install packages
USER root

# install additional package...
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  gnupg python3.7
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub 
RUN apt-key add 7fa2af80.pub
RUN echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" >> /etc/apt/sources.list
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  curl wget patch libcudnn8 cuda-11-4 nvidia-driver-470
# install tensorflow for GPUs
RUN pip install tensorflow-gpu==2.2.0 tensorboard==2.2.0
#RUN pip install git+https://github.com/cliffwoolley/jupyter_tensorboard.git
#RUN pip install git+https://github.com/chaoleili/jupyterlab_tensorboard.git
RUN pip install jupyter-server-proxy jupyter-tensorboard-proxy



# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}