import sys
from trace_shell import TraceShell


def main():
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} path/to/prolog/file')
        return
    shell = TraceShell()
    shell.run(sys.argv[1])


if __name__ == '__main__':
    main()
