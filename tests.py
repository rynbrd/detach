"""Test the detach module."""
import detach
import os
import sys
import tempfile
import time
import unittest
from collections import deque
from multiprocessing import Event, Lock, Queue
from Queue import Empty as QueueEmpty

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

    def setUp(self):
        self.queue = Queue()
        self.put_event = Event()

    def put(self, item):
        """Put an item to the internal queue."""
        self.queue.put(item)

    def put_done(self):
        """Notify when all puts are complete."""
        self.put_event.set()

    def assertQueue(self, want, msg=None, timeout=2):
        """Drain the queue and compare its contents to want."""
        items = []
        self.assertTrue(self.put_event.wait(timeout))
        time.sleep(0.5)
        while not self.queue.empty():
            items.append(self.queue.get())
        self.assertEqual(items, list(want), msg)

    @parentonly
    def test_detach(self):
        """Detach()"""
        try:
            want = deque()
            with detach.Detach(sys.stdout, sys.stderr, sys.stdin) as d:
                if d.pid:
                    want.append(d.pid)
                else:
                    pid = os.getpid()
                    self.put(pid)
                    self.put_done()
            self.assertQueue(want)
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @parentonly
    def test_daemonize(self):
        """Detach(daemonize=True)"""
        try:
            with detach.Detach(sys.stdout, sys.stderr, sys.stdin, daemonize=True) as d:
                pass
            raise Exception("parent did not exist")
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @parentonly
    def test_close_fds(self):
        """Detach(close_fds=True)"""
        try:
            want = deque()
            fd = tempfile.NamedTemporaryFile(delete=False)
            with detach.Detach(sys.stdout, sys.stderr, sys.stdin, close_fds=True) as d:
                if d.pid:
                    fd.close()
                else:
                    self.assertRaises(IOError, fd.close)
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    @parentonly
    def test_exclude_fds(self):
        """Detach(close_fds=True, exclude_fds=[fd])"""
        try:
            want = deque()
            fd = tempfile.NamedTemporaryFile(delete=False)
            with detach.Detach(sys.stdout, sys.stderr, sys.stdin, close_fds=True, exclude_fds=[fd]) as d:
                if d.pid:
                    fd.close()
                else:
                    fd.close()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
