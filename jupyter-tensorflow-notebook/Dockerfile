FROM jupyter/tensorflow-notebook
# Get the latest image tag at:
# https://hub.docker.com/r/jupyter/minimal-notebook/tags/
# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/minimal-notebook/Dockerfile

# Switch to root to install packages
USER root

# install additional package...
RUN apt-get remove --yes python3
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  gnupg 
#python3.8

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub 
RUN apt-key add 7fa2af80.pub
RUN echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" >> /etc/apt/sources.list
#RUN apt-get remove --yes nvidia-driver* 
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  curl wget patch libcudnn8 cuda-11-1 nvidia-driver-460
# install tensorflow for GPUs
#RUN pip install https://files.pythonhosted.org/packages/54/b5/c26b59d86eede0eaa65c88b9021525625351501f43c19f26455f4d2ef31c/tensorflow_gpu-2.2.2-cp38-cp38-manylinux2010_x86_64.whl
RUN pip install tensorflow tensorboard jupyter-server-proxy jupyter-tensorboard-proxy
#RUN pip install git+https://github.com/cliffwoolley/jupyter_tensorboard.git
#RUN pip install git+https://github.com/chaoleili/jupyterlab_tensorboard.git




# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
