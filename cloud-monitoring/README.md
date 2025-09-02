# Cloud Monitoring
------------------

This python package bundles together a collection of cloud monitoring scripts for our OpenStack cloud.

These scripts can be used to collect metrics that will be formatted and pushed to a time-series database. At the moment 
this time-series database is InfluxDB and the monitoring scripts are hardcoded to work only with it.


# Prerequisites

You need to have InfluxDB DB running, and credentials to write to it 
For local testing - you can spin up a local InfluxDB: https://docs.influxdata.com/influxdb/v2/get-started/setup/

You also need admin access to an OpenStack Cloud you're interested in collecting metrics for - from a `clouds.yaml`

Once you've got a DB running and admin credentials, you can copy `monitoring.conf` to the `/tmp` folder
`cp monitoring.conf /tmp/`
and edit it to add InfluxDB hostname, username and password. 

(Optional) If your clouds.yaml file contains multiple cloud accounts, you'll also want to set the cloud config name to use. 
Leave it as default `openstack` if it only contains one.

# Installation
------------------

## Harbor Image

We push a docker image to our harbor instance. 

You can create a docker container and run a script `slottifier.py` by running:
``` docker run --rm harbor.stfc.ac.uk/stfc-cloud/cloud-monitoring:latest \
    --volume /tmp/monitoring.conf:/app/monitoring.conf \
    --volume /tmp/clouds.yaml:/etc/openstack/clouds.yaml \ 
    slottifier
```

## Local Python Package

You can build the python package

```
cd cloud-monitoring
pip install .
python -m cloudMonitoring slottifier /tmp/monitoring.conf
```

## Local Docker Image

```commandline
cd cloud-monitoring
docker build . -t cloud-monitoring:1
```

```commandline
docker run --rm cloud-monitoring:1 \
    --volume /tmp/monitoring.conf:/app/monitoring.conf \
    --volume /tmp/clouds.yaml:/etc/openstack/clouds.yaml \ 
    slottifier
```

# Usage

There are currently 4 different scripts that you can run:

## Slottifier

`python -m cloudMonitoring slottifier /tmp/monitoring.conf`

This script collects slots available for each flavor.
This aims to provide an rough estimate to show what flavor VMs are most available for them to create

The script works by:


1. Calculates the RAM, CPU and GPU requirements for that flavor
2. Calculates the current available RAM and CPU capacity for each hypervisors that can host a VM of that flavor
- NOTE: we're unable to get current available GPU capacity. If the flavor requires a GPU then we make a BIG assumption
that the hypervisor is running only this type of flavor and based on used capacity we work out the number of GPUs available
5. Calculates the maximum number of theoretical VMs could fit on each hypervisor found based on its current capacity
4. Aggregates the total

NOTE: this is an estimation - it makes the assumption that available CPU and RAM is the only requirement for a hypervisor to fit onto that flavor.

## Service Stats

`python -m cloudMonitoring project-stats /tmp/monitoring.conf`

This script collects various quota limits and usage for all openstack projects

## Service Stats

`python -m cloudMonistoring service-stats /tmp/monitoring.conf`

This script collects various service statuses, usages and limits for all hypervisors

## VM States

`python -m cloudMonitoring vm-states /tmp/monitoring.conf`

This script is used to total the number of virtual machines in running, shutoff, errored and build states


# Creating Cron jobs
You can create a cron job like so:
```commandline
sudo tee /etc/cron.d/service-stats.cron > /dev/null << 'EOF'
# run every hour
0 * * * * root docker run --rm harbor.stfc.ac.uk/stfc-cloud/cloud-monitoring:latest \    
    --volume /tmp/monitoring.conf:/app/monitoring.conf \
    --volume /tmp/clouds.yaml:/etc/openstack/clouds.yaml \ 
    slottifier
EOF
```

# Kubernetes Installation
## 1. Prerequisites
You will need:
- A Kubernetes cluster, with access to management via Kubectl
- A configured `monitoring.conf` file
- A `clouds.yaml` file


Create a namespace to isolate the jobs:
``` bash
kubectl create namespace cloud-monitoring
```

## 2. Create Secrets
Upload your configuration files as Kubernetes secrets:

```bash
kubectl create secret generic monitoring-conf-secret \
  --from-file=monitoring.conf=/path/to/monitoring.conf \
  -n cloud-monitoring
```

``` bash
kubectl create secret generic clouds-yaml-secret \
  --from-file=clouds.yaml=/path/to/clouds.yaml \
  -n cloud-monitoring
```
These secrets will be mounted into the containers at runtime.

## 3. Deploy the CronJobs
Apply each CronJob:

``` bash
kubectl apply -f deploy/cronjob-slottifier.yaml -n cloud-monitoring
kubectl apply -f deploy/cronjob-project-stats.yaml -n cloud-monitoring
kubectl apply -f deploy/cronjob-service-stats.yaml -n cloud-monitoring
kubectl apply -f deploy/cronjob-vm-states.yaml -n cloud-monitoring
```

Each job will run hourly (0 * * * *).

## 4. Verify CronJobs
Check that the relevant jobs are scheduled:
``` bash
kubectl get cronjobs -n cloud-monitoring
```

To see the logs of the most recent job, run:
``` bash
kubectl get jobs -n cloud-monitoring  # Find the latest Job created from the CronJob

kubectl logs job/<job-name> -n cloud-monitoring
```