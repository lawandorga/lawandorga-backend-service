import abc
from typing import Type, Union


class Repository(abc.ABC):
    IDENTIFIER: str


class RepositoryWarehouse:
    repositories: dict[str, Type[Repository]] = {}

    @classmethod
    def get(cls, item: Union[str, Type[Repository]]) -> Type[Repository]:
        if isinstance(item, str):
            identifier = item
        elif issubclass(item, Repository):
            identifier = item.IDENTIFIER
        else:
            raise ValueError("The item type does not match.")
        return cls.repositories[identifier]

    @classmethod
    def add_repository(cls, repository: Type[Repository]):
        if (
            repository.IDENTIFIER in cls.repositories
            and cls.repositories[repository.IDENTIFIER] != repository
        ):
            raise ValueError(
                "This or another repository with the same identifier is already in this warehouse."
            )
        cls.repositories[repository.IDENTIFIER] = repository

    @classmethod
    def reset(cls):
        cls.repositories = {}
