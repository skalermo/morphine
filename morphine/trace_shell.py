import sys
import os
import signal
import subprocess
from subprocess import Popen, PIPE
import threading

from morphine.trace_formatter import TraceFormatter


class TraceShell:
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.swipl_p = None
        self.formatter = TraceFormatter()

    def run(self, source_file):
        env = os.environ.copy()
        path = os.path.abspath(source_file)
        command = f'swipl -s {path} -g "leash(-all),trace,start." -t halt'
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, shell=True, env=env)
        self.swipl_p = p
        sys.stdout.write("Started tracing in local terminal...\n\n")

        def writeall(p):
            output = []
            while True:
                data = p.stdout.read(1).decode("utf-8")
                if not data:
                    break
                output.append(data)
                if data == '\n':
                    output_str = ''.join(output)
                    output = []
                    if self.formatter.check_if_prolog_trace(output_str):
                        output_str = self.formatter.format_prolog_trace(output_str)
                    sys.stdout.write(output_str)
                    sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(p,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                self._write(p, d.encode())

        except EOFError:
            pass

    def signal_handler(self, sig, frame):
        self.swipl_p.kill()
        # print(sig, frame)
        print('Interrupted.')
        exit()

    def _write(self, process, message):
        process.stdin.write(message)
        try:
            process.stdin.flush()
        except BrokenPipeError:
            process.kill()
            exit(0)


