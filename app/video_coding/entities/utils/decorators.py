from collections.abc import Callable
from functools import wraps
from typing import Any


def ignore_errors(err_list: list[Exception] = None, default=None) -> Callable:
    """
    Decorator used for ignoring errors
    Returns a default value when an "allowed" exception is raised
    :param err_list: list of allowed exceptions
    :param default: default value to be returned
    :raises: Any type of exception that is not allowed
    """

    def decorator_ignore_errors(func) -> Callable:
        @wraps(func)
        def wrapper_ignore_errors(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if err_list and any(isinstance(e, err_type) for err_type in err_list):
                    return default
                raise e

        return wrapper_ignore_errors

    return decorator_ignore_errors
