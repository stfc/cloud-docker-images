# Deploying Cloud ChatOps
This document covers the following: creating a Slack Workspace and Application, finding / generating Slack and GitHub tokens and deploying the application onto a host. 

> **_NOTE:_** The installation has only been tested on Ubuntu (20.04) Linux Distributions and may need to be modified to work on others such as Rocky Linux.

## Contents:
[Quick Start](#recommended-installation-quick-start)<br>
[Slack Configuration](#slack-configuration)<br>
[Slack Tokens](#slack-tokens)<br>
[Deployment Configuration](#deployment-configuration)<br>
[Deployment](#deployment)<br>

### Recommended Installation (Quick Start):

Below are instructions for the recommended installation.
This uses docker compose and an auto updating script to keep the application on the latest version.<br>

#### Prerequisites:

- Set up Slack Workspace and Application [here](#slack-configuration)
- Retrieved Slack bot user and app tokens[here](#slack-tokens)
- Generated a GitHub personal access token
- Installed Docker and Docker Compose [here](https://docs.docker.com/engine/install/ubuntu/)

#### Installation:

1. Make a directory in `/etc` to store all ChatOps related files. Set group ownership to docker so other users (update script) can access the files.
    ```shell
    # Create directories
    sudo mkdir /etc/chatops
    sudo mkdir /etc/chatops/secrets
    sudo mkdir /etc/chatops/config
    
    # Set permissions
    sudo chown -R $USER:docker /etc/chatops
    sudo chmod 774 /etc/chatops
    sudo chmod 774 /etc/chatops/config
    sudo chmod 770 /etc/chatops/secrets
   
    # Clone repository into directory
    git clone https://github.com/stfc/cloud-docker-images.git /etc/chatops/cloud-docker-images
    ```
2. Edit the `template_config.yml` and `template_secrets.yml` to create your respective config and secrets file. See [here](#deployment-configuration) for more detail.
   ```shell
   # Copy files into secrets folder
   cp /etc/chatops/cloud-docker-images/cloud-chatops/template_config.yml /etc/chatops/config/config.yml
   cp /etc/chatops/cloud-docker-images/cloud-chatops/template_secrets.yml /etc/chatops/secrets/secrets.yml
   
   # If you edited the template_secrets.yml from the cloned repository in /etc/chatops/cloud-docker-images/cloud-chatops
   # You should delete / reset the file as the permissions are too open
   
   git reset --hard origin/master 
   # Or
   rm /etc/chatops/cloud-docker-images/cloud-chatops/template_secrets.yml
   ```
3. Need to add the Ubuntu user to the docker group for the cron script:
   ```shell
   sudo usermod -aG docker ubuntu
   ```
4. Move Cron script and start container:
   ```shell
   # Copy script to etc/cron.< hourly | daily | monthly >
   sudo cp /etc/chatops/cloud-docker-images/cloud-chatops/chatopscron /etc/cron.daily/

   # Check that crontab can see and run the script
   # If the chatops cron file is not in the command output then crontab will not run it
   run-parts --test /etc/cron.daily
   
   # Launch the container and verify set up is correct
   # Using sudo here to mimic crontab which runs as root user
   sudo /etc/cron.daily/chatopscron
   
   # Verify the container is running
   docker ps | grep -i cloud-chatops
   ```

### Slack Configuration:

You will need a Slack Workspace and Slack App.<br>

#### Workspace:
Creating the workspace is simple and can be done by following this documentation [here](https://slack.com/intl/en-gb/help/articles/206845317-Create-a-Slack-workspace). There is no additional setup needed.<br>

#### App:
Creating a Slack App can be done [here](https://api.slack.com/quickstart).<br>
You can copy the application manifest from [app_manifest.yml](./app_manifest.yml) and paste into `Features / App Manifest`.<br>
Alternatively, you can manually set up the following config whilst going through the setup.<br>

> **_NOTE:_** Socket Mode must be enabled before Events and slash commands can be set up. This can be enabled under `Settings / Socket Mode`
- **Features / OAuth & Permissions / Scopes / Bot Token Scopes**:
  - `channels.history`
  - `chat:write`
  - `commands`
  - `groups:history`
  - `reactions:write`
  - `users.profile:read`
  

- **Features / Event Subscriptions / Events / Subscribe to bot events**:
  - `message.channels`
  - `message.groups`
  

- **Features / Slash Commands**:
  - `/prs`
    - description: Get all open PRs
    - usage_hint: "[all: every pr] [mine: your prs]"
    - should_escape: false

### Slack Tokens:

You will need the Slack App and Bot User tokens when deploying the application. When configuring your app at https://api.slack.com/apps/ you can find / generate these tokens.<br>
- App token:
  - You can generate the App token under `Settings / Basic Information / App-Level Tokens`.
  - You will need to give it the scope `connections:write`.
  - The name does not matter, and you **can** retrieve this token at a later date from the same location.


- Bot User Token:
  - You can find the Bot User token under `Settings / Install App / OAuth Tokens`.
  - No scoping is required, and you **can** retrieve this token at a later date from the same location.

### Deployment Configuration:

Two files required for the deployment of this application: `config.yml` and `secrets.yml`.<br>

#### Config:
The application configuration is stored in `config.yml`.
This includes information such as username mapping and repositories to check.<br>
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
```

#### Secrets:
The `secrets.yml` file should look like the below and there is a template [here](template_secrets.yml)
```yaml
  SLACK_BOT_TOKEN: <your-token>
  SLACK_APP_TOKEN: <your-token>
  GITHUB_TOKEN: <your-token>
```
Slack:<br>
- Slack Token information can be found [here](#slack-tokens).<br>

GitHub:<br>
-  A GitHub Personal Access Token is needed to bypass rate limiting and allows access to private repositories.<br>
- Documentation on how to create a GitHub personal access token can be found 
[here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).<br>

### Deployment Options:

The application can be run from a Docker image, source code or Kubernetes<br>


#### Dependencies:
* If running from a Docker image, ensure Docker is installed (see [installation guide](https://docs.docker.com/engine/install/)) and the user account is in the relevant docker users group 
* If running the application from source, ensure Python 3.10 or higher is installed. The full list of required python packages can be found in [requirements.txt](requirements.txt)<br>
* If running on Kubernetes, this documentation only describes how to apply a deployment. You will need a cluster already set up.

> **_NOTE:_** Commands below assume you are in the cloud-chatops folder in the project.

#### Docker image:
 
You can build the image locally or pull from [STFC Harbor](https://harbor.stfc.ac.uk/harbor/projects/33528/repositories/cloud-chatops).<br>
Note: If you are pulling the image you will need to specify a version tag. 
The latest version can be found in [version.txt](version.txt)<br>
- ```shell
  # Local build and run
  docker build -t cloud_chatops cloud-chatops
  docker run cloud_chatops \
  -v <path_to>/secrets.yml/:/usr/src/app/cloud_chatops/secrets/secrets.yml \
  -v <path_to>/config.yml/:/usr/src/app/cloud_chatops/config/config.yml 
  ```
  
- ```shell
  # Pull the image and run, specifying a version
  docker run harbor.stfc.ac.uk/stfc-cloud/cloud-chatops:<version> \
  -v <path_to>/secrets.yml/:/usr/src/app/cloud_chatops/secrets/secrets.yml \
  -v <path_to>/config.yml/:/usr/src/app/cloud_chatops/config/config.yml
  ```
  ```shell
  # Use docker compose (this file will always contain the latest version):
  # You will need to set up the directory structure as shown in the Quick Start.
  # Or edit the docker-compose.yml choosing your own paths
  docker compose up -d
  ```

#### Running from source:
You will need to have the following folder structure for the config and secrets to be accessible:

```markdown
$HOME/dev_cloud_chatops
├── config
│   ├── config.yml
├── secrets
│   ├── secrets.yml

or 

$HOMEPATH/dev_cloud_chatops
├── config
│   ├── config.yml
├── secrets
│   ├── secrets.yml
```

You can run the code from [dev.py](src/dev.py).<br>
It's always recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) 
for the application to run before installing dependencies.


```shell
# Install Venv module
python3 -m venv my_venv
# Activate venv
source my_venv/bin/activate
# Install requirements
pip3 install -r requirements.txt
# Run app
python3 src/dev.py
```

#### Kubernetes Deployment
You will need a running cluster. Run the following commands from your management / control host (the host with your kubeconfig).

1. Clone the repository and create your config / secrets files
   ```shell
   # Start from the Home directory
   cd ~
   git clone https://github.com/stfc/cloud-docker-images.git
   
   # Edit and rename the template config and secrets file described in the "deployment configuration" section
   cd cloud-chatops
   
   vim template_config.yml
   vim template_secrets.yml
   
   mv template_config.yml config.yml
   mv template_secrets.yml secrets.yml
   ```
   
2. Create Kubernetes resources and apply deployment
   ```shell
   # Create Kubernetes resources
   kubectl create namespace cloud-chatops
   kubectl create configmap cloud-chatops-config --from-file config.yml -n cloud-chatops
   kubectl create secret generic cloud-chatops-secrets --from-file secrets.yml -n cloud-chatops
   
   # Apply the deployment
   kubectl apply -f deployment.yml -n cloud-chatops
     
   # Check the status of the pod with
   kubectl get pods -n cloud-chatops # To get pod name
   kubectl logs <pod_name> -n cloud-chatops
   ```
