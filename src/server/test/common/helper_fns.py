import Pyro4
from sh import python3 as _python3
import sh
import sys
import re
from typing import Iterable
import path
import os

_service_procs = []

BASE_PATH = os.environ['PSEDIT_BASE_DIR']


service_dir = path.Path(f'{BASE_PATH}/services')


def snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def python3(*args, **kwargs) -> sh.RunningCommand:
    """ Helper function that starts a script in the background. """
    process = _python3(*args, **kwargs, _bg=True, _out=sys.stdout)
    return process


def start_service(fname: str):
    process = python3(fname)
    _service_procs.append(process)


def start_nameserver():
    process = python3("-m", "Pyro4.naming")
    _service_procs.append(process)


def start_services(*service_list: str, wait=True):
    """ Start services. """
    with service_dir:
        start_service("logger.py")
        for service in service_list:
            start_service(f"{snake(service)}.py")

    if wait:
        wait_for_services(service_list)


def wait_for_services(service_list: Iterable[str]):
    """ Wait until the services are registered with the Pyro name server. """
    ns = Pyro4.locateNS()
    service_set = {f"service.{sname}" for sname in service_list}
    while not (service_set < {k for k, v in ns.list().items()}):
        pass


def start_and_wait(*service_list: str):
    """ Start nameserver, start services, wait. """
    start_nameserver()
    start_services(*service_list)


def kill_services():
    global _service_procs
    for process in _service_procs:
        try:
            process.kill()
        except sh.SignalException_SIGKILL:
            pass
    _service_procs = []
