# Cloud ChatOps
![Build](https://github.com/stfc/cloud-docker-images/actions/workflows/cloud_chatops.yaml/badge.svg)
[![codecov](https://codecov.io/gh/stfc/cloud-docker-images/graph/badge.svg?token=BZEBAE0TQD)](https://codecov.io/gh/stfc/cloud-docker-images)

## Contents:
[About](#about)<br>
[Deployment](#deployment)<br>
[Usage / Features](#usage--features)<br>
[Testing](#testing)<br>

### About

Cloud ChatOps is designed to help encourage developers to complete GitHub/GitLab pull requests.
Either by getting them approved and merged or closed when they go stale.
The app notifies authors about their pull requests in Slack through channels or direct messages.
There are multiple methods of sending these reminders.<br>

### Deployment

For instructions on how to deploy Cloud ChatOps, see [INSTALL.md](INSTALL.md)

### Usage / Features

The main purpose of this app is to remind the team about pull requests they have open across their GitHub repositories or GitLab projects.<br>
This is facilitated by the below features which can be found in [main.py](chatops/main.py).

#### Slash Commands:
These slash commands can be run in any channel the app has access to.<br>
 - `/prs <mine | all>`: sends a private message to the user with a list of open pull requests. Either user authored or by anyone.

#### Scheduled Events:
The app has an endpoint at `https://<your-app-domain>/slack/schedule` which listens for requests to trigger reminder messages being sent.<br>
You must provide the same secret / token that you generated and stored in the [secrets.yml](deployments/template_secrets.yml) file where the app is being hosted.<br>
You must send POST requests like the below:<br>
```bash
curl -X POST \
-H "Content-Type: application/json" \
-H "Authorization: token myToken" \
--data '{"type":"global | personal", "channel": "ABC123CD45"}' \
https://<your-app-domain>/slack/schedule
```
This triggers either of the below functions depending on the value of "type". Using "global" requires you to provide a channel ID.<br>
Defined in the [events.py](chatops/events.py) module:<br>
- `run_global_reminder()`: sends a message to the pull request channel with every open pull request across the repositories in a thread.

- `run_personal_reminder()`: sends a message to each user, in the config map, directly with a thread of their open pull requests.

### Health check
The app has a health check endpoint at `https://<your-app-domain>/health` which will return "200, OK" if the app is up. 
```bash
curl -X GET https://<your-app-domain>/health
```

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
Considering this, you need to make a development Slack app mirroring the production app.
You also need to change any member / channel IDs in the config to those of the development workspace.

Integration tests should be developed / run alongside unit tests when working on the code.<br>
They offer the benefit of end-to-end functional testing inside a development environment / workspace.<br> 
Integration tests are run from [dev.py](chatops/dev.py) using flags to specify which tests to run.<br>
`dev.py` always runs the Slack app after the tests so you can test the slash commands.<br>

E.g.
```shell
# See the help message for information
python3 chatops/dev.py --help

# Test a specific event e.g. global reminders
python3 chatops/dev.py --global --channel "some_test_channel"

# Test another event e.g. personal reminders
python3 chatops/dev.py --personal

# To test multiple events
python3 chatops/dev.py --global --personal --channel "some_test_channel"

# To test only slash commands
python3 chatops/dev.py # Then run slash commands in Slack
```
