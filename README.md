# Piconet

Remote control server with built-in web interface and command-line tool for picoscopes.

## Prerequisites

First you need to have Pico SDK installed in your system. For that check out [pico website](https://www.picotech.com/downloads)

## Installation

For development run `pip install -e .` in the root folder of the repository.

TODO: publish on pip

## Usage

The project provides an RPC server and a command-line interface.

### Starting the server

TODO

```sh
piconetd
```

### Configuration and command-line arguments

TODO

### Using `piconet-cli`

```sh
# check out the cli help:
piconet-cli --help
# list available devices:
piconet-cli list
```

## Development environment

Create a virtual environment and install the module in developer mode:

```sh
virtualenv .venv
source .venv/bin/activate
pip install -e .
```

Install dev requirements and hooks to enforce black:

```sh
pip install -r dev_requirements.txt
pre-commit install
```

Run tests from the root of the repo:

```sh
pytest
```

