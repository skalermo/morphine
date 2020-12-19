"""Console script for morphine."""
import argparse
import sys

from morphine.trace_shell import TraceShell


def main():
    """Console script for morphine."""
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_file', type=str, help='Path to Prolog file to run and trace')
    args = parser.parse_args()

    TraceShell().run(args.path_to_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
