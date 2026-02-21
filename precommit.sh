#!/bin/bash

export PIPENV_VERBOSITY=-1
export PIPENV_QUIET=1

printf "\nisort:\n" && uv run isort . --profile black
printf "\n\n"
printf "black:\n" && uv run black .
printf "\n\n"
printf "ruff:\n"  && uv run ruff check . --fix
printf "\n\n"
printf "mypy:\n"  && uv run mypy .
printf "\n\n"
