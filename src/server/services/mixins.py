import Pyro4


class LoggerMixin:
    def __init__(self, logger):
        self._logger: Pyro4.Proxy = logger

        self._logname = 'unnamed logger'

    def _log(self, level: str, msg: str, *args, **kwargs):
        getattr(self._logger, level)(self._logname, msg, args, kwargs)

    def _info(self, *args, **kwargs):
        return self._log('info', *args, **kwargs)

    def _error(self, *args, **kwargs):
        return self._log('error', *args, **kwargs)

    def _warning(self, *args, **kwargs):
        return self._log('warning', *args, **kwargs)

    def _debug(self, *args, **kwargs):
        return self._log('debug', *args, **kwargs)
