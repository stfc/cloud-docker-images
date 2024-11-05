# Cloud ChatOps
![Build](https://github.com/stfc/cloud-docker-images/actions/workflows/cloud_chatops.yaml/badge.svg)
[![codecov](https://codecov.io/gh/stfc/cloud-docker-images/graph/badge.svg?token=BZEBAE0TQD)](https://codecov.io/gh/stfc/cloud-docker-images)

## Contents:
[About](#about)<br>
[Usage / Features](#usage--features)<br>
[Deployment](#deployment)<br>

### About

Cloud ChatOps is designed to help encourage developers to complete GitHub pull requests. 
Either by getting them approved and merged or closed when they go stale.<br>
The app will notify authors about their pull requests, usually by Slack, until they are closed / merged. There are multiple methods of sending these reminders.<br>

### Usage / Features

The main purpose of this application is to remind the team about pull requests they have open across their GitHub repositories.<br>
This is facilitated by the below features which can be found in [main.py](src/main.py).

#### Slash Commands:
These slash commands can be run in any channel the application has access to.<br>
 - `/prs <mine | all>`: Sends a private message to the user with a list of open pull requests. Either user authored or by anyone.

#### Scheduled Events:
Using the [schedule](https://pypi.org/project/schedule/) library functions are triggered on a weekly basis.<br>
Events are defined in the `main.py/schedule_jobs` function:<br>
- `run_global_reminder()`: Sends a message to the pull request channel with every open pull request across the repositories in a thread.
- `run_personal_reminder()`: Sends a message to each user directly with a thread of their open pull requests.

### Deployment

For instructions on how to deploy Cloud ChatOps, see [INSTALL.md](./INSTALL.md)
