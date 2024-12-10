# Cloud ChatOps
![Build](https://github.com/stfc/cloud-docker-images/actions/workflows/cloud_chatops.yaml/badge.svg)
[![codecov](https://codecov.io/gh/stfc/cloud-docker-images/graph/badge.svg?token=BZEBAE0TQD)](https://codecov.io/gh/stfc/cloud-docker-images)

## Contents:
[About](#about)<br>
[Deployment](#deployment)<br>
[Usage / Features](#usage--features)<br>
[Testing](#testing)<br>

### About

Cloud ChatOps is designed to help encourage developers to complete GitHub pull requests. 
Either by getting them approved and merged or closed when they go stale.<br>
The app will notify authors about their pull requests, usually by Slack, until they are closed / merged. There are multiple methods of sending these reminders.<br>

### Deployment

For instructions on how to deploy Cloud ChatOps, see [INSTALL.md](./INSTALL.md)

### Usage / Features

The main purpose of this application is to remind the team about pull requests they have open across their GitHub repositories.<br>
This is facilitated by the below features which can be found in [main.py](src/main.py).

#### Slash Commands:
These slash commands can be run in any channel the application has access to.<br>
 - `/prs <mine | all>`: Sends a private message to the user with a list of open pull requests. Either user authored or by anyone.
 - `/find-host`: Responds with the IP of the host running the app

#### Scheduled Events:
Using the [schedule](https://pypi.org/project/schedule/) library functions are triggered on a weekly basis.<br>
The dates and times when the events are run are hard coded in [events.py/schedule_jobs](src/events.py)<br>
Events are defined in the [events.py](src/events.py) module:<br>
- `run_global_reminder()`: Sends a message to the pull request channel with every open pull request across the repositories in a thread.
    - Runs on: Monday / Wednesday @ 09:00 UTC
- `run_personal_reminder()`: Sends a message to each user (in the config map) directly with a thread of their open pull requests.
    - Runs on: Monday @ 09:00 UTC

### Testing
#### Unit Tests

Unit tests are stored in the [tests](tests) directory.<br>
Each Python module should have a test module named after it `test_<python_module>`and test functions are named `test_<function_name>`.<br>
Unit tests are run in the GitHub workflow but should be run locally before pushing changes. Again, we recommend using Python Venvs<br>
```shell
# From the cloud_chatops folder
python3 -m venv my_venv
source my_venv/bin/activate
pip3 install -r requirements.txt
python3 -m pytest tests

# Or to show coverage in the terminal use:
python3 -m pytest tests --cov-report xml:coverage.xml --cov
python3 -m pycobertura show coverage.xml
```

#### Integration Tests

**Integration tests should be run in a development Slack workspace not the main Cloud workspace.**
Considering this, you will need to make a development Slack application mirroring the production application.
You will also need to change any member / channel IDs in the config to those of the development workspace.

Integration tests should be developed / run alongside unit tests when working on the code.<br>
They offer the benefit of end-to-end functional testing inside a development environment / workspace.<br> 
Integration tests are run from [dev.py](src/dev.py) using flags to specify which tests to run.<br>
`dev.py` will always run the Slack application after the tests so you can test the slash commands.<br>

E.g.
```shell
# See the help message for information
python3 src/dev.py --help

# Test a specific event e.g. global reminders
python3 src/dev.py --global --channel "some_test_channel"

# Test another event e.g. personal reminders
python3 src/dev.py --personal

# To test multiple events
python3 src/dev.py --global --personal --channel "some_test_channel"

# To test only slash command
python3 src/dev.py # Then run slash commands in Slack
```
