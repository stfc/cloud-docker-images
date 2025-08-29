# Cloud Monitoring
------------------

This python package bundles together a collection of cloud monitoring scripts for our openstack cloud.

These scripts can be used to collect metrics that will be formatted and pushed to a time-series database. At the moment 
this time-series database is influxDB and the monitoring scripts are hardcoded to work only with it.


# Prerequisites

You need to have influxDB DB running, and credentials to write to it 
For local testing - you can spin up a local influxdb: https://docs.influxdata.com/influxdb/v2/get-started/setup/

You also need admin access to a Openstack Cloud you're interested in collecting metrics for - from a `clouds.yaml`

Once you've got a DB running and admin credentials, you can copy `monitoring.conf` to the `/tmp` folder
`cp monitoring.conf /tmp/`
and edit it to add influxdb hostname, username and password. 

(Optional) If you're clouds.yaml contains multiple cloud accounts - you'll also want to set the cloud config name to use. 
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