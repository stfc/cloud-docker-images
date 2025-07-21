# Deploying Cloud ChatOps
This document covers the following: creating a Slack Workspace and app, finding / generating Slack and GitHub tokens and deploying the app onto a host. 

> **_NOTE:_** The installation has only been tested on Ubuntu (22.04) and may need to be modified to work on others such as Rocky Linux.

## Contents:
[Slack Configuration](#slack-configuration)<br>
[Deployment Configuration](#deployment-configuration)<br>
[Deployment](#deployment)<br>
[Development](#developing-new-features)<br>

### Slack Configuration:

You need a Slack Workspace and Slack App.<br>

#### Workspace:
Creating the workspace is straightforward and can be done by following this documentation [here](https://slack.com/intl/en-gb/help/articles/206845317-Create-a-Slack-workspace). There is no additional setup needed.<br>

#### App:
1. Creating a Slack App can be done [here](https://api.slack.com/quickstart).<br>
2. Copy the app manifest below and paste into `Features / App Manifest`.<br>
   ```yaml
   display_information: # Change me!
     name: Cloud ChatOps
     description: Cloud teams ChatOps integration
     background_color: "#004d8d"
   features:
     bot_user:
       display_name: Cloud ChatOps
       always_online: true
     slash_commands:
       - command: /prs
         url: https://<your-domain-here>/slack/events # Change me!
         description: "To find work that you've created, or all open pull requests."
         usage_hint: "[all: every open PR] [mine: created, assigned or requested PRs]"
         should_escape: false
   oauth_config:
     scopes:
       bot:
         - channels:history
         - chat:write
         - commands
         - groups:history
         - reactions:write
         - users.profile:read
   settings:
     org_deploy_enabled: false
     socket_mode_enabled: false
     token_rotation_enabled: false
   ```
3. This copies all necessary config however you want to change:
   - The display information and name
   - The `slash_commands` url domain

### Slack Tokens:

You need the Bot Token and Signing Secret when deploying the app.
When configuring your app at https://api.slack.com/apps/ you can find / generate these tokens.<br>

- Bot User Token:
  - You can find the Bot User token under `Settings / Install App / OAuth Tokens`.
  - No scoping is required, and you **can** retrieve this token at a later date from the same location.
  
- Signing Secret:
  - You can find the Signing Secret under `Settings / Basic Information / Client Secret`

- App token (only needed for development):
  - You can generate the App token under `Settings / Basic Information / App-Level Tokens`.
  - You need to give it the scope `connections:write`.
  - The name doesn't matter, and you **can** retrieve this token at a later date from the same location.

### Deployment Configuration:

Two config files required for the deployment of this app: `config.yml` and `secrets.yml`.<br>

#### Config:
The app configuration is stored in `config.yml`.
This includes information such as username mapping and repositories to check.<br>
Slack Channel and Member IDs can be found in Slack by:<br>
- Right-clicking the member / channel
- View member / channel details
- Near the bottom of the About tab there will be an ID with copy button

The `config.yml` should look like this:
```yaml
---
app:  # Configuration for the app
  users:
    - realName: Real Name
      slackID: slack_id
      githubName: github_username
      gitlabName: gitlab_username


github:  # Configuration for the GitHub feature
  enabled: true  # Disable if you do not want GitHub pull request reminders
  repositories:
    <owner>:
      - <repo>

gitlab:  # Configuration for the GitLab feature
  enabled: true  # Disable if you do not want GitHub pull request reminders
  domain: gitlab.example.com
  projects:
    <group>:
      - <project>

```

#### Secrets:
The `secrets.yml` file should look like:
```yaml
---
SLACK_BOT_TOKEN: <your-token> # Required

# You must have either of the app token or signing secret.
SLACK_APP_TOKEN: <your-token> # Development use only
SLACK_SIGNING_SECRET: <your-token> # Production use only

SCHEDULED_REMINDER_TOKEN: <your-token> # Optional: to use the endpoint /slack/schedule reminder
GITHUB_TOKEN: <your-token> # Optional: to find GitHub pull requests
GITLAB_TOKEN: <your-token> # Optional: to find GitLab merge requests
```

Slack:<br>
- Slack Token information can be found [here](#slack-tokens).<br>

GitHub:<br>
-  A GitHub Personal Access Token is needed to bypass rate limiting and allows access to private repositories.<br>
- Documentation on how to create a GitHub personal access token can be found 
[here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).<br>

GitLab:<br>
- A GitLab Personal Access Token is needed to authenticate with the GitLab API.
- Documentation on how to create a GitLab personal access token can be found
[here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)<br>

### Deployment:

You **must** have a publicly accessible and trusted endpoint to receive traffic from Slack. This means opening a port in
your firewall, an appropriate DNS record and using Let's Encrypt or another certificate provider.

As the ChatOps application runs a HTTP server, you will need a load balancer or reverse proxy to provide the HTTPS 
connection. This documentation provides a Docker compose file with HAProxy as the reverse proxy.

An example HAProxy config file for HTTPS is provided below:
```
global
  log stdout format raw local0 info

defaults
  mode http
  timeout client 10s
  timeout connect 5s
  timeout server 10s
  timeout http-request 10s
  log global

frontend public
  bind :80
  bind :443 ssl crt /usr/local/etc/haproxy/tls.crt
  http-request redirect scheme https unless { ssl_fc }
  default_backend slackapps

backend slackapps
  # option forwardfor
  server slackapp chatops:3000
```

#### Requirements:
- Set up Slack Workspace and app [here](#slack-configuration)
- Prepared the `config.yml` and `secrets.yml` files
- Installed Docker and Docker Compose [here](https://docs.docker.com/engine/install/ubuntu/)
- DNS record, public IP address with port 443 open and SSL certificate
- Config files created [here](#config)

#### Installation:

1. Make a directory in `/opt` to store all ChatOps related files.
    ```shell
    # Create directory
    sudo mkdir /opt/chatops
    sudo chown $USER:$USER /opt/chatops
    cd /opt/chatops
   
    # Copy config files
    cp -t . <path-to>/config.yml <path-to>/secrets.yml <path-to>/haproxy.cfg <path-to>/tls.crt 
       
    # Set permissions
    sudo chmod 644 config.yml haproxy.cfg
    sudo chmod 600 secrets.yml tls.crt
   
    # Clone repository into directory
    git clone https://github.com/stfc/cloud-docker-images.git
    ```

2. Start docker compose to bring up the stack
   ```shell
   # Make sure you are in the cloned repository
   cd /opt/chatops/cloud-docker-images
   
   # Start the containers
   docker compose up -d
   ```

## Developing new features:

When developing new features, it's easier to run the app locally to test new changes.
To do this, we use Socket mode.
This means we don't have to expose any endpoints with untested changes and minimal security.
You need to have the following folder structure for the config and secrets to be accessible:

To make sure you have the configuration set up correctly, follow [Deployment Configuration](#deployment-configuration)

```markdown
Unix like systems:

$HOME/dev_cloud_chatops
├── config.yml
├── secrets.yml

or 

Windows:

$HOMEPATH/dev_cloud_chatops
├── config.yml
├── secrets.yml
```

You can run the code from [dev.py](chatops/dev.py) which starts the Slack app.<br>
It's always recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) before installing dependencies.

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
