FROM python:3.10

WORKDIR /usr/src/app

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    krb5-user \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AQ_PREFIX=NOT_SET \
    AQ_URL=NOT_SET\
    #
    KRB5CCNAME=NOT_SET \
    #
    RABBIT_HOST=NOT_SET \
    RABBIT_PORT=NOT_SET \
    RABBIT_USERNAME=NOT_SET \
    RABBIT_PASSWORD=NOT_SET\
    #
    OPENSTACK_AUTH_URL=NOT_SET \
    OPENSTACK_COMPUTE_URL=NOT_SET \
    OPENSTACK_USERNAME=NOT_SET \
    OPENSTACK_PASSWORD=NOT_SET

ENV LOG_LEVEL=INFO

CMD [ "python", "./entrypoint.py"]
