
FROM jupyter/tensorflow-notebook:ubuntu-22.04

RUN pip install jupyter-server-proxy tensorflow tensorboard --no-cache-dir
RUN pip install gym==0.25.2 pygame --no-cache-dir

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
