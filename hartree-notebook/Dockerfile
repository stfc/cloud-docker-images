
FROM jupyter/tensorflow-notebook:ubuntu-22.04

# Switch to root to install packages
USER root

RUN apt-get update --yes \
    && apt-get install --yes curl wget patch \
    && rm -rf /var/lib/apt/lists/*

# https://gitlab.com/hartreetraining1/hartree-data-science-training
COPY requirements.txt /etc
RUN pip install --no-cache-dir -r /etc/requirements.txt

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}
