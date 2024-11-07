# Deploying Cloud ChatOps
This document details the instructions to install dependencies and run the ChatOps application

## Contents:
[Requirements](#requirements)<br>
[Deployment](#deployment)<br>

### Requirements:

Two files required for the deployment of this application: `config.yml` and `secrets.json`.<br>
These should be stored in `$HOME/cloud_chatops_secrets/` on the host system.<br>

#### Config:
The application configuration is stored in [config.yml](template_config.yml).
This includes information such as username mapping, repositories to check and default values.<br>
Slack Channel and Member IDs can be found in Slack by:<br>
- Right-clicking the member / channel
- View member / channel details
- Near the bottom of the About tab there will be an ID with copy button

The `config.yml` should look like the below:
```yaml
---
maintainer: <maintainers_member_id>

user-map:
  <user_github_username>: <user_member_id>

repos:
  <organisation>:
    - <repo>

defaults:
  author: <author_member_id>
  channel: <reminder_channel_id>
```
#### Secrets:
The `secrets.json` file should look like the below and there is a template [here](template_secrets.json)
```json
{
  "SLACK_BOT_TOKEN": "<your-token>",
  "SLACK_APP_TOKEN": "<your-token>",
  "GITHUB_TOKEN": "<your-token>"
}
```
Slack:<br>
- TODO: How to create your own Slack application.<br>

GitHub:<br>
-  A GitHub Personal Access Token is needed to bypass rate limiting and allows access to private repositories.<br>
- Documentation on how to create a GitHub personal access token can be found 
[here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).<br>


### Deployment:
The application can be run from a Docker image or source code. (Assuming running from project root)<br>

#### Dependencies:
* If running from a Docker image, ensure Docker is installed (see [installation guide](https://docs.docker.com/engine/install/)) and the user account is in the relevant docker users group 
* If running the application from source, ensure Python 3.10 or higher is installed. The full list of required python packages can be found in [requirements.txt](requirements.txt)<br>

#### Docker image:
You can build the image locally or pull from [STFC Harbor](https://harbor.stfc.ac.uk/harbor/projects/33528/repositories/cloud-chatops).<br>
Note: If you are pulling the image you will need to specify a version tag. 
The latest version can be found in [version.txt](version.txt)<br>
- ```shell
  # Local build and run
  docker build -t cloud_chatops cloud-chatops
  docker run -v $HOME/cloud_chatops_secrets/:/usr/src/app/cloud_chatops_secrets/ cloud_chatops
  ```
- ```shell
  # First log in to harbor
  docker login -u <username> harbor.stfc.ac.uk
  
  # Then either:
  
  # Run container directly, specifying a version
  docker run -v $HOME/cloud_chatops_secrets/:/usr/src/app/cloud_chatops_secrets/ harbor.stfc.ac.uk/stfc-cloud/cloud-chatops:<version>
  #
  # or
  #
  # Use Docker Compose in cloud-chatops folder, which will always contain latest image version
  docker compose up -d
  ```

#### Running from source:
You can run the code from [main.py](src/main.py).<br>
It's always recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) 
for the application to run before installing dependencies.
- ```shell
  # Install Venv module
  python3 -m venv my_venv
  # Activate venv
  source my_venv/bin/activate
  # Install requirements
  pip3 install -r requirements.txt
  # Run app
  python3 cloud-chatops/src/main.py prod
  ```

### Automatic Container Update

To pull the latest `docker-compose` file automatically, you can copy the `chatopscron` file into any of the `cron.< hourly | daily | weekly | monthly > directories found in `/etc`.

Once created, you will need to change the file permissions accordingly:

```shell
  # Change into repo directory
  cd cloud-docker-images/cloud-chatops

  # Change permissions on script
  chmod +x chatopscron

  # Copy script to etc/cron.<timeframe>
  sudo cp chatopscron /etc/cron.<timeframe>

  # You can test that the script is running correctly by using this command.
  run-parts /etc/cron.<timeframe>

  #if you don't recieve any output, the script has not run.
  ```

*Please note when naming the file within /etc/cron.<timeframe> you cannot use file extenstions. Only valid characters are allowed [a-zA-Z]*