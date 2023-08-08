
FROM jupyter/tensorflow-notebook:ubuntu-22.04

# pip install required packages
RUN pip install jupyter-server-proxy tensorflow==2.11.1 tensorboard --no-cache-dir 
RUN pip install gym==0.25.2 pygame --no-cache-dir

# Note, the trailing slash is important!
ENV TENSORBOARD_PROXY_URL=/user-redirect/proxy/6006/
