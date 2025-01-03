# sources:
# - https://github.com/jupyter/docker-stacks
# - https://github.com/TomographicImaging/CIL#installation-of-cil
# TODO: use `ubuntu-22.04` once `cil` adds `python=3.11` support
FROM jupyter/tensorflow-notebook:ubuntu-20.04

RUN mamba install -y -c conda-forge -c intel -c ccpi \
  cil=23.0.1 astra-toolbox tigre ccpi-regulariser tomophantom "ipywidgets<8" \
  jupyter-server-proxy \
  && mamba clean -a -y -f \
  && fix-permissions "${CONDA_DIR}" \
  && fix-permissions "/home/${NB_USER}"

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
