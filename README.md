# Tasks Management Bot

This is an internal WEBA IT project to allow tasks management via Telegram Bot interface.

## Development environment set up

* Clone the project
* Copy the *config.env.sample* to *config.env*
* Fill in the values in *config.env*

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
