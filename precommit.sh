#!/bin/bash

export PIPENV_VERBOSITY=-1
export PIPENV_QUIET=1

printf "\nisort:\n" && pipenv run isort . --profile black
printf "\n\n"
printf "black:\n" && pipenv run black .
printf "\n\n"
printf "flake8:\n"  && pipenv run flake8 .
printf "\n\n"
printf "ruff:\n"  && pipenv run ruff check .
printf "\n\n"
printf "mypy:\n"  && pipenv run mypy .
printf "\n\n"
