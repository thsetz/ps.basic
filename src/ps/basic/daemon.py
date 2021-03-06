"""Generic linux daemon base class for python 3.x."""

import atexit
import os
import signal
import sys
import time


class Daemon:
    """A generic daemon class.

    import os
    import sys
    from ps.basic.daemon import daemon
    from ps.herald.ps_bridge import main
    os.environ["DEV_STAGE"] = "DEVELOPMENT"

    class MyDaemon(daemon):
        def run(self):
            sys.argv[0] = "ps_bridge"
            sys.argv[1] = "-v"
            sys.stdout = open('ps_bridge.olog', 'a+')
            sys.stderr = open('ps_bridge.elog', 'a+')
            main()


    if __name__ == "__main__":
        daemon = MyDaemon("/tmp/ps_bridge.pid")
        if len(sys.argv) == 2:
            if "start" == sys.argv[1]:
                daemon.start()
            elif "stop" == sys.argv[1]:
                daemon.stop()
            elif "restart" == sys.argv[1]:
                daemon.restart()
            else:
                print("Unknown command")
                sys.exit(2)
            sys.exit(0)
        else:
            print("usage: %s start|stop|restart" % sys.argv[0])
            sys.exit(2)
    """

    def __init__(self, pidfile):
        """Set the name of the pidfile."""
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize the process."""
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #1 failed: {err}\n")
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #2 failed: {err}\n")
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        fd_in = open(os.devnull, "r")
        fd_out = open(os.devnull, "a+")
        fd_err = open(os.devnull, "a+")

        os.dup2(fd_in.fileno(), sys.stdin.fileno())
        os.dup2(fd_out.fileno(), sys.stdout.fileno())
        os.dup2(fd_err.fileno(), sys.stderr.fileno())

        # create pidfile
        pid = str(os.getpid())
        with open(self.pidfile, "w+") as fp:
            fp.write(pid + "\n")

        # register del_pid to be called on exit
        atexit.register(self.delpid)

    def delpid(self):
        """Delete the pidfile."""
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""
        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile, "r") as fp:
                pid = int(fp.read().strip())
        except IOError:
            pid = None

        if pid:
            message = f"pidfile {self.pidfile} already exist. "
            message += "Daemon already running?\n"
            sys.stderr.write(message)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""
        # Get the pid from the pidfile
        try:
            with open(self.pidfile, "r") as fp:
                pid = int(fp.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = f"pidfile {self.pidfile} does not exist. "
            message += "Daemon not running?\n"
            sys.stderr.write(message)
            return

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """Xecute the provided function.

        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by
        start() or restart().
        """
