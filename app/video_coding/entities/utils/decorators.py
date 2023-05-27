from functools import wraps


def ignore_errors(err_list: list[Exception] = None):
    def decorator_ignore_errors(func):
        @wraps(func)
        def wrapper_ignore_errors(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if err_list and any(isinstance(e, err_type) for err_type in err_list):
                    return None
                raise e

        return wrapper_ignore_errors

    return decorator_ignore_errors
