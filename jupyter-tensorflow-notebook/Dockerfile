  
FROM jupyter/tensorflow-notebook:python-3.8.8
# Get the latest image tag at:
# https://hub.docker.com/r/jupyter/minimal-notebook/tags/
# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/minimal-notebook/Dockerfile

# Switch to root to install packages
USER root

# install additional package...
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  gnupg
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub 
RUN apt-key add 7fa2af80.pub
RUN echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" >> /etc/apt/sources.list
RUN apt-get remove --yes nvidia* *cuda*
#RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  curl wget patch libcudnn8 cuda-11-1 nvidia-driver-470
RUN apt-get  --allow-unauthenticated update --yes && apt-get --allow-unauthenticated install --yes  curl wget patch cuda-toolkit-11-1 libcudnn8
# install tensorflow for GPUs
RUN pip uninstall tensorflow tensorboard --yes
RUN pip install tensorflow-gpu tensorboard
RUN pip install jupyter-server-proxy
RUN pip install jupyterlab --upgrade



# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
ENV TENSORBOARD_PROXY_URL=/proxy/6006
