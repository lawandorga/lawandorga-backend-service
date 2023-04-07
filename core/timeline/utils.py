import re

PATTERN = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake_case(camel: str):
    snake = PATTERN.sub(r"\1_\2", camel).lower()
    return snake
