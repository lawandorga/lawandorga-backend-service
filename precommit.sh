#!/bin/bash

printf "\nisort:\n" && isort . --profile black
printf "\n\n"
printf "black:\n" && black .
printf "\n\n"
printf "flake8:\n"  && flake8 .
printf "\n\n"
printf "ruff:\n"  && ruff check .
printf "\n\n"
printf "mypy:\n"  && mypy .
printf "\n\n"
