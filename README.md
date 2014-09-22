Detach
======
Fork and detach the current process.

[![Build Status](https://travis-ci.org/BlueDragonX/detach.svg)](https://travis-ci.org/BlueDragonX/detach)

Usage
-----
The `detach` package contains a context manager called `Detach`. It is used
with `with` statement to fork the current process and execute code in that
process. The child process exits when the context manager exits. The following
parameters may be passed to `Detach` to change its behavior:

* `stdout` - Redirect child stdout to this stream.
* `stderr` - Redirect child stderr to this stream.
* `stdin` - Redirect his stream to child stdin.
* `close_fds` - Close all file descriptors in the child excluding stdio.
* `exclude_fds` - Do not close these file descriptors if close_fds is `True`.
* `daemonize` - Exit the parent process when the context manager exits.

Examples
--------
### Simple Fork with STDOUT

    import detach, os, sys

    with detach.Detach(sys.stdout) as d:
        if d.pid:
            print("forked child with pid {}".format(d.pid))
        else:
            print("hello from child process {}".format(os.getpid()))

### Daemonize 

    import detach
    from your_app import main

    def main():
        """Your daemon code here."""

    with detach.Detach(daemonize=True) as d:
        if d.pid:
            print("started process {} in background".format(pid))
        else:
            main()

### Call External Command

    import detach, sys
    pid = detach.call(['bash', '-c', 'echo "my pid is $$"'], stdout=sys.stdout)
    print("running external command {}".format(pid)) 
    

License
-------
Copyright (c) 2014 Ryan Bourgeois. This project and all of its contents is
licensed under the BSD-derived license as found in the included [LICENSE][1]
file.

[1]: https://github.com/bluedragonx/detach/blob/master/LICENSE "LICENSE"
