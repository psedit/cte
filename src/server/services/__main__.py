import sys
import traceback
import importlib

try:
    module_to_start = sys.argv[1]
except IndexError:
    print(f"Usage: python3 -m services <service_name>")
    sys.exit()

try:
    mod = importlib.import_module(f".{sys.argv[1]}", "services")
except ImportError:
    print(f"Error: failed to import module '{sys.argv[1]}', does that "
          f"service exist?")
    sys.exit()

try:
    mod.main()
except AttributeError:
    traceback.print_exc()
    print(f"Error: module '{sys.argv[1]}' has no main function - is it a "
          f"service?")
