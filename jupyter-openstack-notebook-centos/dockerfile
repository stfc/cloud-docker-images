FROM harbor.stfc.ac.uk/stfc-cloud/jupyter-base-notebook-centos:latest
# Switch to root to install packages
USER root

# install additional package...
RUN yum update -y && yum install -y curl wget patch

#Install OpenstackCLI

RUN mamba install --quiet --yes \
    'python-openstackclient'\
    'python-magnumclient'\
    'python-octaviaclient'\
    'python-novaclient'\
    'aodhclient'\
    'openstacksdk' && \
    mamba clean --all -f -y

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}