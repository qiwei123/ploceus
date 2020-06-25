# -*- coding: utf-8 -*-
import errno
import fcntl
import os
import pprint
from queue import Empty, Queue
import subprocess
from threading import Thread
import warnings

from ploceus.common import get_current_context
from ploceus.colors import cyan, green, yellow
from ploceus.exceptions import LocalCommandError, RemoteCommandError
from ploceus.runtime import env
from ploceus.logger import log, LOGGER


__all__ = ['run', 'sudo']


class CommandResult(object):

    def __init__(self, stdout, stderr, exitvalue):
        self.stdout = stdout
        self.stderr = stderr
        self.exitvalue = exitvalue

    def __repr__(self):
        return '<#CommandResult %s>' % self.status()

    def status(self):
        if self.failed:
            return 'failed'
        return 'succeeded'

    @property
    def failed(self):
        return self.exitvalue != 0

    @property
    def succeeded(self):
        return self.exitvalue == 0

    @property
    def ok(self):
        return self.succeeded


def nb_fd_readline(fd):
    """non-blocking readline from fd

    Args:
        fd (int): file descriptor to read from

    Returns:
        string, int: line, status
            status: 0  a new line
            status: -1 not a new line
    """
    line = b''
    while True:
        try:
            _ = os.read(fd, 1)
            line += _
            if _ == b'\n':
                return line, 0
            if _ == b'\r':
                _ = os.read(fd, 1)
                return line, 0
        except OSError as e:
            try:
                if type(e) == BlockingIOError:
                    return line, -1
                else:
                    raise
            except NameError:
                if e.errno == errno.EAGAIN:
                    return line, -1
                else:
                    raise


def run_in_child(cmd, env):
    # nb_fd_readline will drain CPU
    # return run_in_child_fork(cmd, env)
    return run_in_child_subprocess(cmd, env)


def run_in_child_subprocess(cmd, env):
    """
    run child process using subprocess
    threading for non-blocking polling stdout, stderr

    pros: simpler code
    cons: do not guarantee output order
    """
    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env)

    def enqueue_data(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    outQ = Queue()
    errQ = Queue()
    t1 = Thread(target=enqueue_data, args=(p.stdout, outQ))
    t1.daemon = True
    t2 = Thread(target=enqueue_data, args=(p.stderr, errQ))
    t2.daemon = True
    t1.start()
    t2.start()

    while True:
        rc = p.poll()
        if rc is not None:
            break
        try:
            out = outQ.get(timeout=.05)
        except Empty:
            pass
        else:
            yield out, None, rc

        try:
            err = errQ.get(timeout=.05)
        except Empty:
            pass
        else:
            yield None, err, rc

    t1.join()
    t2.join()

    while True:
        try:
            out = outQ.get(timeout=.05)
        except Empty:
            break
        else:
            yield out, None, rc

    while True:
        try:
            err = errQ.get(timeout=.05)
        except Empty:
            break
        else:
            yield None, err, rc

    yield None, None, rc


def run_in_child_fork(cmd, env):
    """run shell command in child process,
    non-blocking yields output.

    pros: output in order, somehow
    cons: complex code

    Args:
        cmd (string): command to run
        env (dict): environment variables

    Returns:
        bytes, bytes, int: stderr, stderr and exit value,
            output would be ``None'',
            exit value should use the last one.

    """
    LOGGER.debug('env: {}'.format(pprint.pformat(env)))

    outr, outw = os.pipe()
    errr, errw = os.pipe()
    pid = os.fork()

    exitvalue = None
    if pid == 0:
        # child
        os.dup2(outw, 1)
        os.dup2(errw, 2)

        os.close(outr)
        os.close(outw)
        os.close(errr)
        os.close(errw)

        os.execle('/bin/bash', 'bash', '-c', cmd, env)
    else:
        f = fcntl.fcntl(outr, fcntl.F_GETFL)
        fcntl.fcntl(outr, fcntl.F_SETFL, f | os.O_NONBLOCK)
        f = fcntl.fcntl(errr, fcntl.F_GETFL)
        fcntl.fcntl(errr, fcntl.F_SETFL, f | os.O_NONBLOCK)

        outline = b''
        errline = b''
        while True:
            _, s = nb_fd_readline(outr)
            if _ and s == 0:
                outline += _
                yield outline, None, exitvalue
                outline = b''
                continue
            if _ and s == -1:
                outline += _

            _, s = nb_fd_readline(errr)
            if _ and s == 0:
                errline += _
                yield None, errline, exitvalue
                errline = b''
                continue
            if _ and s == -1:
                errline += _

            try:
                _pid, exitvalue = os.waitpid(-1, os.WNOHANG)
            except OSError as e:
                if e.errno == errno.ECHILD:
                    break

        outline = b''
        while True:
            _, s = nb_fd_readline(outr)
            if _ and s == 0:
                outline += _
                yield outline, None, exitvalue
                outline = b''
                continue
            if _ and s == -1:
                outline += _
            if not _:
                yield outline, None, exitvalue
                break
        errline = b''
        while True:
            _, s = nb_fd_readline(errr)
            if _ and s == 0:
                errline += _
                yield None, errline, exitvalue
                errline = b''
                continue
            if _ and s == -1:
                errline += _
            if not _:
                yield None, errline, exitvalue
                break


def run(command, quiet=False, _raise=True,
        silence=False, *args, **kwargs):
    # TODO: global sudo

    if not command:
        raise ValueError('empty command')

    _, stdout, stderr, rc = _run_command(
        command, quiet, _raise, silence)
    return CommandResult(stdout, stderr, rc)


def sudo(command, quiet=False, _raise=True,
         sudo_user=None, silence=False):
    if sudo_user:
        command = 'sudo -u %s -H %s' % (sudo_user, command)
    else:
        command = 'sudo -H %s' % (command)
    return run(command, quiet, _raise, silence)


def local(command, quiet=False, _raise=True, silence=False, _env=None):

    if not command:
        raise ValueError('empty command')

    context = get_current_context()

    if _env is None:
        _env = dict(os.environ)

    cwd = context.get('cwd')
    if cwd:
        command = 'cd "%s" && %s' % (cwd, command)

    if not silence:
        log(command, prefix=cyan('run[local]'))

    stdout = []
    stderr = []
    exitvalue = 0
    for outline, errline, exitvalue in run_in_child(command, _env):
        if outline:
            line = outline.decode(env.encoding).strip()
            stdout.append(line)
            if not quiet and not env.keep_quiet:
                log(line.strip(), prefix=green('stdout'))
        if errline:
            line = errline.decode(env.encoding).strip()
            stderr.append(line)
            if not quiet and not env.keep_quiet:
                log(line.strip(), prefix=yellow('stderr'))

    stdout = '\n'.join(stdout)
    stderr = '\n'.join(stderr)

    LOGGER.debug('local exitvalue: {}'.format(exitvalue))

    if exitvalue != 0:
        if _raise:
            raise LocalCommandError(
                'stdout: %s\n\nstderr: %s' % (stdout, stderr))

    return CommandResult(stdout, stderr, exitvalue)


def _run_command(command, quiet=False, _raise=True, silence=False):
    context = get_current_context()

    client = context.get_client()
    wrapped_command = command

    if context.get('cwd'):
        wrapped_command = 'cd %s && %s' % (context.get('cwd'), command)

    environment = None
    if context.get('env'):
        environment = context.get('env')
        LOGGER.debug('environment: {}'.format(environment))

    def cb(line, tag):
        if quiet:
            return
        if env.keep_quiet:
            return
        if tag == 'err':
            log(line.strip(), prefix=yellow('stderr'))
        else:
            log(line.strip(), prefix='stdout')

    if not silence:
        log(wrapped_command, prefix=cyan('run'))

    real_command = wrapped_command
    if environment:
        env_pair = []
        for k, v in environment.items():
            env_pair.append('{}={}'.format(k, v))
        real_command = 'export {} && {}'.format(
            ' '.join(env_pair), wrapped_command)

    LOGGER.debug('run real_command: {}'.format(real_command))

    stdin, stdout, stderr, rc = client.exec_command(
        real_command, output_callback=cb)

    # stdout = stdout.decode(env.encoding)
    # stderr = stderr.decode(env.encoding)

    if rc != 0 and _raise:
        raise RemoteCommandError(
            'stdout: %s\n\nstderr: %s' % (stdout, stderr))

    return stdin, stdout, stderr, rc
