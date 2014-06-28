"""Fork and detach the current process."""
import errno
import os
import resource
import subprocess
import sys
import traceback
from multiprocessing import Value

maxfd = 2048


class Error(Exception):
    """Raised on error."""


class Detach(object):

    def __init__(self, stdout=None, stderr=None, stdin=None, close_fds=False, exclude_fds=None,
                 daemonize=False):
        """
        Fork and detach a process. The stdio streams of the child default to /dev/null but may be
        overridden with the `stdout`, `stderr`, and `stdin` parameters. If `close_fds` is True then
        all open file descriptors (except those passed as overrides for stdio) are closed by the
        child process. File descriptors in `exclude_fds` will not be closed. If `daemonize` is True
        then the parent process exits.
        """
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.close_fds = close_fds
        self.exclude_fds = set()
        self.daemonize = daemonize
        self.pid = None
        self.shared_pid = Value('i', 0)

        for item in list(exclude_fds or []) + [stdout, stderr, stdin]:
            if hasattr(item, 'fileno'):
                item = item.fileno()
            self.exclude_fds.add(item)

    def _get_max_fd(self):
        """Return the maximum file descriptor value."""
        limits = resource.getrlimit(resource.RLIMIT_NOFILE)
        result = limits[1]
        if result == resource.RLIM_INFINITY:
            result = maxfd
        return result

    def _close_fd(self, fd):
        """Close a file descriptor if it is open."""
        try:
            os.close(fd)
        except OSError, exc:
            if exc.errno != errno.EBADF:
                msg = "Failed to close file descriptor {}: {}".format(fd, exc)
                raise Error(msg)

    def _close_open_fds(self):
        """Close open file descriptors."""
        maxfd = self._get_max_fd()
        for fd in reversed(range(maxfd)):
            if fd not in self.exclude_fds:
                self._close_fd(fd)

    def _redirect(self, stream, target):
        """Redirect a system stream to the provided target."""
        if target is None:
            target_fd = os.open(os.devnull, os.O_RDWR)
        else:
            target_fd = target.fileno()
        os.dup2(target_fd, stream.fileno())

    def __enter__(self):
        """Fork and detach the process."""
        pid = os.fork()
        if pid > 0:
            # parent
            os.waitpid(pid, 0)
            self.pid = self.shared_pid.value
        else:
            # first child
            os.setsid()
            pid = os.fork()
            if pid > 0:
                # first child
                self.shared_pid.value = pid
                os._exit(0)
            else:
                # second child
                if self.close_fds:
                    self._close_open_fds()

                self._redirect(sys.stdout, self.stdout)
                self._redirect(sys.stderr, self.stderr)
                self._redirect(sys.stdin, self.stdin)
        return self

    def __exit__(self, exc_cls, exc_val, exc_tb):
        """Exit processes."""
        if self.daemonize or not self.pid:
            if exc_val:
                traceback.print_exception(exc_cls, exc_val, exc_tb)
            os._exit(0)


def call(args, stdout=None, stderr=None, stdin=None, daemonize=False,
         preexec_fn=None, shell=False, cwd=None, env=None):
    """
    Run an external command in a separate process and detach it from the current process. Excepting
    `stdout`, `stderr`, and `stdin` all file descriptors are closed after forking. If `daemonize`
    is True then the parent process exits. All stdio is redirected to `os.devnull` unless
    specified. The `preexec_fn`, `shell`, `cwd`, and `env` parameters are the same as their `Popen`
    counterparts. Return the PID of the child process if not daemonized.
    """
    stream = lambda s, m: s is None and os.open(os.devnull, m) or s
    stdout = stream(stdout, os.O_WRONLY)
    stderr = stream(stderr, os.O_WRONLY)
    stdin = stream(stdin, os.O_RDONLY)

    shared_pid = Value('i', 0)
    pid = os.fork()
    if pid > 0:
        os.waitpid(pid, 0)
        child_pid = shared_pid.value
        del shared_pid
        if daemonize:
            sys.exit(0)
        return child_pid
    else:
        os.setsid()
        proc = subprocess.Popen(args, stdout=stdout, stderr=stderr, stdin=stdin, close_fds=True,
                                preexec_fn=preexec_fn, shell=shell, cwd=cwd, env=env)
        shared_pid.value = proc.pid
        os._exit(0)
