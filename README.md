# gitea-py

Manage organizations, teams and permissions in Gitea (Code platform).

## Requirements

* `Python >= 3.6`
* Gitea credentials (user, token and URL)

## Install

Export as env variables: `GITEA_URL`, `GITEA_TOKEN` and `GITEA_ADMIN_USER`

Production

For production systems we use binary file. Ask or build the binary.

Development

* `pip install pipenv`
* `pipenv install --dev`

## Usage

Production

* Create new config file (examples [here](examples))
* Run `giteapy run -f your_config_file.yaml` to apply the config
* Run `giteapy --help` for active commands and options

Development

* Create new config file (examples [here](examples))
* Run `pipenv run giteapy --help` or `pipenv shell` and execute commands in there

Build executable

* `pipenv run tox -e package` (depends of the operating system)

## Tests

Not yet.

## Authors

[Marius Stanca](mailto:me@marius.xyz)
