# Update IAM Roles

## About

Update IAM roles is a script that we use to run on a Cron job on one of our service nodes. The script adds IAM users to their projects via roles. This repo is the result of us containarising the script to make it easier to deploy and redeploy, while having some alerting on the container itself.

### Deployment

Deployment is done via Kayobe, therefore grab yourself a kayobe environment if you don't already have one.

Instructions on creating and accessing a new Kayobe environment can be found here [Setting up a Kayobe Environment](https://stfc.atlassian.net/wiki/spaces/SC/pages/762806304/Setting+up+a+Kayobe+environment?xpis=eyJicmlkZ2UiOiJzZWFyY2hQYWdlIiwiaWQiOiIxNzkwMDk0OTk1MDMyIiwic291cmNlIjoiY29uZmx1ZW5jZSJ9).

Either source your prod or dev env:

`source <path-to-your-kayobe-env/env-vars.sh>`

And run the ansible playbook:

`kayobe playbook run ansible/deploy-iam-roles-update-container.yml`

This will create the container on the first service node in the list using `hosts: controllers[0]`. You will be able to see which node it chooses when the playbook runs.

### Logging

To see if the container is running, SSH on to the service node and run:

`docker ps | grep "iam"`
and
`docker logs <container-id>`

You should see no errors. Yay.

Otherwise, you may need to fix the errors.

