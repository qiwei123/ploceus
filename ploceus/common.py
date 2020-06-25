# -*- coding: utf-8 -*-
import warnings

from ploceus.utils.collections import ThreadLocalRegistry
from ploceus.utils.local import LocalStack

# bottom level module can be safely import by any other modules
# DO NOT import internal modules directly at top level
# !! UNLESS is is ABSOLUTELY SAFE !!

# proxy storage for Scope instances...
# intented for multi-threading usage, so ThreadingLocal()
scope_registry = ThreadLocalRegistry(lambda: Scope())


class Scope(dict):
    """
    top level scope for internal usage

    It is intented for tracking for TaskExecutor context
    like a stack for nested situation.
    """
    def __init__(self):
        self.stack = LocalStack()

    @property
    def top(self):
        return self.stack.top

    def push(self, v):
        return self.stack.push(v)

    def pop(self):
        return self.stack.pop()


def get_current_context():
    """
    get current Context for helper function
    """
    scope = get_current_scope()
    rv = scope.top
    if rv is None:
        # FIXME:
        msg = ('should not using any scope/context-awared function '
               'in bare python code')
        warnings.warn(msg)

        from ploceus.context import Context
        rv = Context()
    return rv


def get_current_scope():
    """
    magic GLOBAL STATIC function for get current scope,
    using ThreadingLocal

    It's even valid to use in a multi-threading context.

    t1 = threading.Thread(
        target=run_task, args=(task1, ['localhost', 'remote'],))
    t2 = threading.Thread(
        target=run_task, args=(task1, ['localhost', 'remote'],))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    """
    return scope_registry()
