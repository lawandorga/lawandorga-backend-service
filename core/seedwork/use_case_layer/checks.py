from core.seedwork.use_case_layer.error import UseCaseError


def __check_actor(args, kwargs, func_code, type_hints):
    if len(func_code.co_varnames) == 0 or "__actor" not in func_code.co_varnames:
        raise ValueError("The use case function needs to have '__actor' as input.")

    if "__actor" not in type_hints:
        raise ValueError("The usecase needs a type hint to '__actor'.")

    if "__actor" in kwargs:
        actor = kwargs["__actor"]
    elif len(args) > 0:
        index = func_code.co_varnames.index("__actor")
        actor = args[index]
    else:
        raise ValueError(
            "You need to submit an '__actor' when you call a use case function."
        )

    usecase_actor_type = type_hints["__actor"]
    if not isinstance(actor, usecase_actor_type):
        raise TypeError(
            "The submitted use case '__actor' type is '{}' but should be '{}'.".format(
                type(actor), usecase_actor_type
            )
        )

    return actor


def check_permissions(actor, permissions, message_addition=""):
    assert isinstance(permissions, list)
    for permission in permissions:
        if not actor.has_permission(permission):
            message = "You need the permission '{}' to do this.".format(permission)
            if message_addition:
                message = "{} {}".format(message, message_addition)
            raise UseCaseError(message)
