from sh import python3
import sys

if __name__ == '__main__':
    print("Ready to start test suite")
    python3('-m', 'pytest', 'test', _out=sys.stdout)

