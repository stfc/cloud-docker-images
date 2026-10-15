FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY update-iam-roles.py ./

RUN mkdir -p /etc/openstack

RUN useradd --create-home --shell /bin/bash iam-roles-update
RUN chown -R iam-roles-update:iam-roles-update /app
USER iam-roles-update

CMD [ "python", "./update-iam-roles.py"]