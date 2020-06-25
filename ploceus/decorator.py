# -*- coding: utf-8 -*-
import ploceus.task


def task(*args, **kwargs):
    invoked = bool(not args or kwargs)
    task_class = kwargs.pop('task_class', ploceus.task.Task)

    if not invoked:
        func, args = args[0], ()

    def wrapper(func):
        if isinstance(func, task_class):
            return func

        # define a Task instance (register into global store)
        rv = task_class(func, *args, **kwargs)
        # return the origin func for nested decorator
        return rv

    return wrapper if invoked else wrapper(func)
