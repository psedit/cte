import Pyro4
import logging
import coloredlogs
import functools
import signal
import sys


LOGLEVEL = logging.INFO
FORMAT = "[%(asctime)s] [%(levelname)7s] %(name)7s: %(message)s"


def handler(*args):
    print("Received signal, exiting...")
    sys.exit()


signal.signal(signal.SIGUSR1, handler)


def logsetup(filename, format, loglevel):
    fh = logging.FileHandler(filename)
    fh.setLevel(loglevel)

    sh = logging.StreamHandler()
    sh.setLevel(loglevel)

    formatter = coloredlogs.ColoredFormatter(fmt=format, field_styles={
        "hostname": {"color": "blue"},
        "programname": {"color": "cyan"},
        "name": {"color": "red"},
        "levelname": {"color": "magenta"},
        "asctime": {"color": "cyan"}
    })

    sh.setFormatter(formatter)

    # If you also want the file to have color codes in it
    # fh.setFormatter(formatter)

    logging.basicConfig(handlers=[sh, fh], level=LOGLEVEL)


logsetup("server.log", FORMAT, LOGLEVEL)


def logname_to_logger(fn):
    @functools.wraps(fn)
    def new_fn(self, logname, msg, args, kwargs):
        return fn(self, logging.getLogger(logname), msg, *args, **kwargs)
    return new_fn


@Pyro4.expose
class Logger():
    @logname_to_logger
    def debug(self, logger, msg, *args, **kwargs):
        logger.debug(msg, *args, **kwargs)

    @logname_to_logger
    def info(self, logger, msg, *args, **kwargs):
        logger.info(msg, *args, **kwargs)

    @logname_to_logger
    def warning(self, logger, msg, *args, **kwargs):
        logger.warning(msg, *args, **kwargs)

    @logname_to_logger
    def error(self, logger, msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)


def main():
    log = Logger()
    Pyro4.Daemon.serveSimple({
            log: "meta.Logger",
        }, ns=True)


if __name__ == '__main__':
    main()
