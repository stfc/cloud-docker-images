# Cloud ChatOps
![Build](https://github.com/stfc/cloud-docker-images/actions/workflows/cloud_chatops.yaml/badge.svg)
[![codecov](https://codecov.io/gh/stfc/cloud-docker-images/graph/badge.svg?token=BZEBAE0TQD)](https://codecov.io/gh/stfc/cloud-docker-images)

## Contents:
[About](#about)<br>
[Usage / Features](#usage--features)<br>
[Deployment](#deployment)<br>
[requirements](#requirements)<br>

### About

Cloud ChatOps is designed to help promote the closing of GitHub pull requests. Either by getting them approved and merged or closed when they go stale.<br>
The app will notify authors about their pull requests until they are closed / merged. There are multiple methods of sending these reminders.<br>

### Usage / Features

The main purpose of this application is to remind the team about pull requests they have open across their GitHub repositories.<br>
This is facilitated by the below features which can be found in [main.py](src/main.py).

#### Slash Commands:
These slash commands can be run in any channel the application has access to.<br>
 - `/prs <mine | all>`: Sends a private message to the user with a list of open pull requests. Either user authored or by anyone.

#### Scheduled Events:
Using the [schedule](https://pypi.org/project/schedule/) library functions are triggered on a weekly basis.<br>
Events are defined in the `schedule_jobs` function:<br>
- `run_global_reminder()`: Sends a message to the pull request channel with every open pull request across the repositories in a thread.
- `run_personal_reminder()`: Sends a message to each user directly with a thread of their open pull requests.

### Deployment

Secrets should always be stored in `$HOME/cloud_chatops_secrets` on the host system. Find out more about secrets [here](#Secrets)<br>
The application can be run from a Docker image or source code. (Assuming running from project root)<br>

#### Docker image:
You can build the image locally or pull from [STFC Harbor](https://harbor.stfc.ac.uk).<br>
Note: If you are pulling the image you will need to specify a version tag. 
The latest version can be found in [version.txt](version.txt)<br>
- ```shell
  # Local build and run
  docker build -t cloud_chatops cloud-chatops
  docker run -v $HOME/cloud_chatops_secrets/:/usr/src/app/cloud_chatops_secrets/ cloud_chatops -d
  ```
- ```shell
  # Pull from harbor and run
  docker run -v $HOME/cloud_chatops_secrets/:/usr/src/app/cloud_chatops_secrets/ harbor.stfc.ac.uk/stfc-cloud/cloud-chatops:<version> -d
  ```

#### Running from source:
You can run the code from [main.py](src/main.py).<br>
It's always recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) 
for the application to run before installing dependencies.
- ```shell
  source my_venv/bin/activate
  pip3 install -r requirements.txt
  python3 cloud-chatops/src/main.py prod
  ```






### Requirements:

Two files required for the deployment of this application: `config.yml` and `secrets.json`.<br>
These should be stored in `$HOME/cloud_chatops_secrets` on the host system.<br>

#### Config
The application configuration is stored in [config.yml](template_config.yml).
This includes information such as username mapping, repositories to check and default values.<br>
The `config.yml` should look like the below:
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
#### Secrets

The application needs secrets for Slack and GitHub.<br>
TODO: How to run your own Slack application or find on slack marketplace.<br>
A GitHub Personal Access Token is needed to bypass rate limiting and allows access to private repositories.<br>
Documentation on how to create a GitHub personal access token can be found 
[here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).<br>
The `secrets.json` file should look like the below and there is a template [here](template_secrets.json)
```json
{
  "SLACK_BOT_TOKEN": "<your-token>",
  "SLACK_APP_TOKEN": "<your-token>",
  "GITHUB_TOKEN": "<your-token>"
}
```
