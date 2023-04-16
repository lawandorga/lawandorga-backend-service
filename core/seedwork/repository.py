import abc
from typing import Any, Type, TypeVar, Union


class Repository(abc.ABC):
    IDENTIFIER: str


T = TypeVar("T", bound=Repository)


class RepositoryWarehouse:
    repositories: dict[str, Type[Any]] = {}

    @classmethod
    def get(cls, item: Union[str, Type[T]]) -> Type[T]:
        if isinstance(item, str):
            identifier = item
        elif issubclass(item, Repository):
            identifier = item.IDENTIFIER
        else:
            raise ValueError("The item type does not match.")
        return cls.repositories[identifier]

    @classmethod
    def add_repository(cls, repository: Type[T]):
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
