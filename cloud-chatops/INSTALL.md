# Deploying Cloud ChatOps
This document details the instructions to install dependencies and run the ChatOps application

## Contents:
[Slack Configuration](#slack-configuration)<br>
[Requirements](#requirements)<br>
[Deployment](#deployment)<br>

### Slack Configuration:

You will need a Slack Workspace and Slack App.<br>

#### Workspace:
Creating the workspace is simple and can be done by following this documentation [here](https://slack.com/intl/en-gb/help/articles/206845317-Create-a-Slack-workspace). There is no additional setup needed.<br>

#### App:
Creating a Slack App can be done [here](https://api.slack.com/quickstart). You will need to setup the following features whilst going through the setup.<br>
> **_NOTE:_** Socket Mode must be enabled before Events can be Subscribed to. This can be enabled under `Settings / Socket Mode`
- Scopes:
  - `channels.history`
  - `chat:write`
  - `commands`
  - `groups:history`
  - `reactions:write`
  - `users.profile:read`
- Events / Bot Events:
  - `message.channels`
  - `message.groups`

### Requirements:

Two files required for the deployment of this application: `config.yml` and `secrets.json`.<br>
These should be stored in `$HOME/cloud_chatops_secrets/` on the host system.<br>

#### Config:
The application configuration is stored in `config.yml`.
This includes information such as username mapping, repositories to check and default values.<br>
Slack Channel and Member IDs can be found in Slack by:<br>
- Right-clicking the member / channel
- View member / channel details
- Near the bottom of the About tab there will be an ID with copy button

The `config.yml` should look like the below there is a template without the comments [here](./template_config.yml):
```yaml
---
maintainer: AB12CD34  # Slack Member ID of the application maintainer

user-map:  # Dictionary of GitHub username to Slack Member ID
  my_github_username: AB12CD34
  other_github_username: EF56GH78

repos:  # Dictionary of owners and repositories
  organisation1:
    - repo1  # E.g. github.com/organisation1/repo1
    - repo2
    - repo3
  organisation2:
    - repo1  # E.g. github.com/organisation2/repo1
    - repo2
    - repo3

defaults:  # Default values for application variables
  # Default author will be assigned to pull requests where the PR author is not in the above user map.
  # Usually team lead or senior staff member.
  author: WX67YZ89  # Slack member ID
  
  # Default channel is where the pull requests will be posted.
  # It's recommended to set this as a "maintenance" / "dev" channel in case the application goes awry.
  # The actual channel messages are sent to can be specified in the code.
  channel: CH12NN34  # Slack channel ID
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

To pull the latest `docker-compose` file automatically, you can copy the `chatopscron` file into any of the `cron.< hourly | daily | weekly | monthly >` directories found in `/etc`.

> **_NOTE:_** When naming the file within /etc/cron.\<timeframe> you cannot use file extenstions. Only valid characters are allowed [a-zA-Z]*

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
