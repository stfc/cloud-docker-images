Openstack Rabbit Consumers
---------------------------

The script will monitor the rabbit consumers, and automatically register machines
with the configuration management tool.

This container assumes that a sidecar container is running to handle krb5 machine authentication.

Release
-------

Pull requests will push a tagged image (with the commit sha) to 
harbor.stfc.ac.uk/stfc-cloud-staging/openstack-rabbit-consumer:sha

(Where the SHA can be found in the GH actions build logs)

To release a new version, update version.txt with the updated version.
When the PR is merged, a new image will be pushed to harbor.stfc.ac.uk/stfc-cloud-staging/openstack-rabbit-consumer

You may need to update the version in the helm chart to match the new version.

Testing Locally
===============

Initial setup
-------------

- Spin up minikube locally
- Install the secrets, as per the instructions in the chart
- Make docker use the minikube docker daemon in your current shell:

Testing
-------

- Build the docker image locally:
`eval $(minikube docker-env)`
`docker build -t rabbit-consumer:1 .`
- cd to the chart directory:
`cd ../charts/rabbit-consumer`
- Install/Upgrade the chart with your changes:
`helm install rabbit-consumers . -f values.yaml -f dev-values.yaml -n rabbit-consumers`
- To deploy a new image, rebuild and delete the existing pod:
`docker build . -t rabbit-consumer:n . && helm upgrade rabbit-consumers . -f values.yaml -f prod-values.yaml -n rabbit-consumers`
- Logs can be found with:
`kubectl logs deploy/rabbit-consumers -n rabbit-consumers`

