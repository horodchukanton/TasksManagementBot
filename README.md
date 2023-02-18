# Tasks Management Bot

This is an internal WEBA IT project to allow tasks management via Telegram Bot interface.

## Development environment set up

* Clone the project
* Copy the *config.env.sample* to *config.env*
* Fill in the values in *config.env*


### Using docker-compose environment

Install [docker-compose](https://docs.docker.com/compose/install/)

Enter the `docker` folder

    ```$ cd docker```

Bring up the docker-compose services:
    ```$ docker-compose up -d odoo postgres-app```

Odoo should be available on http://127.0.0.1:8069/

Finish Odoo database creation and generate the API key.

Create a Telegram bot using Bot Father (name doesn't matter).

Use the following values in your config.env:
```
BOT_API_TOKEN = <your Telegram bot token>
DB_DSN = 'postgres://odoo:odoo@127.0.0.1:5433/weba_tasks_management'

ODOO_URL = 'http://127.0.0.1:8069'
ODOO_DATABASE = 'odoo'
ODOO_API_KEY = '<generated API key>'
ODOO_API_LOGIN = '<insert admin email>'
```


### Running tests locally:

#### pytest

To run and write the tests install the module and dev dependencies

    $ pip install -e .
    $ pip install -r requirements_dev.txt
    $ pytest

#### black

[Black](https://black.readthedocs.io/en/stable/) Runs checks for the code style

    $ pip install black
    $ black src tests --check --diff

#### tox

[Tox](https://tox.wiki/en/stable/) allows to run tests and lint checks in separate environments

Install `tox`:

    $ pip install tox

Run `tox`:

    $ tox
