import Pyro4
from sh import python3 as _python3, kill
import sh

_service_pids = []

def python3(*args, **kwargs) -> sh.RunningCommand:
    """ Helper function that starts a script in the background. """
    process = _python3(*args, **kwargs, _bg=True)
    return process

def start_service(fname: str):
    process = python3(fname)
    _service_pids.append(process.pid)

def start_nameserver():
    process = python3("-m", "Pyro4.naming")
    _service_pids.append(process.pid)

def start_services(*service_list: List[str], wait=True):
    """ Start services. """
    with service_dir:
        start_service("logger.py")
        for service in service_list:
            start_service(f"{snake(service)}.py")

    if wait:
        wait_for_services(service_list)

def wait_for_services(service_list: List[str]):
    """ Wait until the services are registered with the Pyro name server. """
    ns = Pyro4.locateNS()
    service_set = {f"service.{sname}" for sname in service_list}
    while not (service_list < {k for k, v in ns.list().items()}):
        pass

def start_and_wait(*service_list: List[str]):
    """ Start nameserver, start services, wait. """
    start_nameserver()
    start_services(*service_list)

def kill_services():
    global _service_pids
    for pid in _service_pids:
        kill('-9', str(pid))
    _service_pids = []
