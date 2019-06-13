import Pyro4
from functools import partial


class LoggerMixin:
    def __init__(self, logger):
        self._logger: Pyro4.Proxy = logger

        for log_method in ('info', 'debug', 'warning', 'error'):
            setattr(self, f'_{log_method}', partial(self._log, log_method))

        self._logname = 'unnamed logger'

    def _log(self, level: str, msg: str, *args):
        getattr(self._logger, level)(self._logname, msg, args)
