import time
import logging
import functools
from threading import Thread


def timer(out=logging.info):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            out("time used: {:g} seconds".format(end - start))

        return wrapper

    return decorator


def limit(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rc = Exception('{}: {:g} seconds exceeded'
                           .format(func.__name__, timeout))

            def new_func():
                nonlocal rc
                try:
                    rc = func(*args, **kwargs)
                except Exception as err_a:
                    rc = err_a

            t = Thread(target=new_func)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as err_b:
                print('error starting thread')
                raise err_b

            if isinstance(rc, BaseException):
                raise rc
            return rc

        return wrapper

    return decorator


def progressive(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None

            @limit(timeout)
            def new_func():
                nonlocal result
                max_d = kwargs.pop('max_depth')
                for depth in range(max_d + 1):
                    try:
                        result = func(*args, max_depth=depth, **kwargs)
                    except Exception as err_a:
                        result = err_a

            try:
                new_func()
            except Exception as _:
                pass

            raise Exception(result)

        return wrapper

    return decorator

