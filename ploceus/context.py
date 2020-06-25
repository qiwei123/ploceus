# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os


from ploceus.common import get_current_context


# FIXME: move to common
class Context(dict):
    """
    context for single task execution
    """

    def __init__(self, *args, **kwargs):
        self.sshclient = None
        super().__init__(*args, **kwargs)
        # FIXME: use property instead
        self['extra_vars'] = {}

        self.hostname = '<missing>'

    def get_client(self):
        if not self.sshclient._connected:

            username = self['username']
            hostname = self.hostname
            password = self['password']

            from ploceus.runtime import env
            gateway = env.gateway_settings.get(hostname)

            username = self.sshclient.connect(
                hostname,
                username=username,
                password=password,
                gateway=gateway)

            self['username'] = username

        return self.sshclient


class ContextManager(object):
    """
    Somehow deprecated usage, for compatibility purpose

    context_manager.get_context()
    """
    def get_context(self):
        """
        get task execution context

        context is now in "/scope_stack/task_ident/..."
        """
        return get_current_context()


def cd(path):

    context = get_current_context()

    path = path.replace(' ', '\ ')
    if 'cwd' in context and \
       not path.startswith('/') and \
       not path.startswith('~'):
        new_cwd = os.path.join(context['cwd'], path)
    else:
        new_cwd = path

    return _setenv('cwd', new_cwd)


def use_env(env):
    return _setenv('env', env)


@contextmanager
def _setenv(name, value):

    context = get_current_context()

    previous = context.get(name)
    context[name] = value
    err = None
    try:
        yield
    except Exception as e:
        err = e

    if previous:
        context[name] = previous
    else:
        context[name] = None

    if err is not None:
        raise err
