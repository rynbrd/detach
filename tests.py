"""Test the detach module."""
import detach
import os
import sys
import tempfile
import time
import unittest

parent_pid = os.getpid()


def parentonly(func):
    """Only execute the decorated function in the parent thread."""
    def wrapper(*args, **kwargs):
        pid = os.getpid()
        if pid == parent_pid:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


class TestDetach(unittest.TestCase):
    """Test the `Dispatch` class."""

    @parentonly
    def test_detach(self):
        """Detach()"""
        fd = tempfile.NamedTemporaryFile(delete=False)
        try:
            want_pid = None
            with detach.Detach(None, sys.stderr, None) as d:
                if d.pid:
                    want_pid = d.pid
                else:
                    pid = os.getpid()
                    fd.write(str(pid))
                    fd.close()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

        time.sleep(0.5)
        fd.seek(0)
        have_pid = int(fd.read())
        fd.close()
        self.assertEqual(want_pid, have_pid)
        os.unlink(fd.name)

    @parentonly
    def test_daemonize(self):
        """Detach(daemonize=True)"""
        fd = tempfile.NamedTemporaryFile(delete=False)
        try:
            with detach.Detach(None, sys.stderr) as d1:
                if not d1.pid:
                    with detach.Detach(None, sys.stderr, None, daemonize=True) as d2:
                        if not d2.pid:
                            fd.close()
                    fd.write('parent is still running')
                    fd.close()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

        time.sleep(0.5)
        fd.seek(0)
        self.assertEqual('', fd.read())
        fd.close()
        os.unlink(fd.name)

    @parentonly
    def test_close_fds(self):
        """Detach(close_fds=True)"""
        fd = tempfile.NamedTemporaryFile(delete=False)
        try:
            with detach.Detach(None, sys.stderr, None, close_fds=True) as d:
                if not d.pid:
                    self.assertRaises(IOError, fd.close)
        except SystemExit as e:
            self.assertEqual(e.code, 0)

        fd.close()
        os.unlink(fd.name)

    @parentonly
    def test_exclude_fds(self):
        """Detach(close_fds=True, exclude_fds=[fd])"""
        try:
            fd = tempfile.NamedTemporaryFile(delete=False)
            with detach.Detach(None, sys.stderr, None, close_fds=True, exclude_fds=[fd]) as d:
                if d.pid:
                    fd.close()
                else:
                    fd.close()
        except SystemExit as e:
            self.assertEqual(e.code, 0)

        os.unlink(fd.name)


class TestCall(unittest.TestCase):
    """Test `call` function."""

    @parentonly
    def test_call(self):
        """call()"""
        fd = tempfile.NamedTemporaryFile(delete=False)
        try:
            want_pid = detach.call(['bash', '-c', 'echo "$$"'], stdout=fd)
            time.sleep(0.5)
            fd.seek(0)
            have_pid = int(fd.read().strip())
            self.assertEqual(have_pid, want_pid)
            fd.close()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        os.unlink(fd.name)
