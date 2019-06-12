import Pyro4
import logging
import coloredlogs
import functools


LOGLEVEL = logging.INFO
FORMAT = "[%(asctime)s] [%(levelname)7s] %(name)7s: %(message)s"


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
    def new_fn(self, logname, msg, args):
        return fn(self, logging.getLogger(logname), msg, *args)
    return new_fn


@Pyro4.expose
class Logger():
    @logname_to_logger
    def debug(self, logger, msg, *args):
        logger.debug(msg, *args)

    @logname_to_logger
    def info(self, logger, msg, *args):
        logger.info(msg, *args)

    @logname_to_logger
    def warning(self, logger, msg, *args):
        logger.warning(msg, *args)

    @logname_to_logger
    def error(self, logger, msg, *args):
        logger.error(msg, *args)


if __name__ == '__main__':
    log = Logger()
    Pyro4.Daemon.serveSimple({
            log: "meta.Logger",
        }, ns=True)
