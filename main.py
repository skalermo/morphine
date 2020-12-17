import sys
import os
import subprocess
from colors import color_print, bcolors


def run_prolog(source_file):
    path = os.path.abspath(source_file)
    command = f'swipl -s {path} -g "leash(-all),trace,start." -t halt'
    result = subprocess.run([c.strip('"') for c in command.split()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.decode('utf-8')


def preprocess_line(line: str):
    if line.startswith('ERROR'):
        return 'ERROR', -1, line[7:]
    split = line[3:].split(maxsplit=2)
    if len(split) != 3:
        print(split)
        return None, 0, ''
    todo, depth, instruc = split
    return todo[:-1], int(depth.strip('()')), instruc


def parse_for_predicate(pred: str, instruc: str):
    args = instruc.split(pred)
    return pred, len(args)


def parse_instruction(instruc: str):
    for pred in ['\\=', '>=']:
        if pred in instruc:
            return parse_for_predicate(pred, instruc)
    if 'is' in instruc.split():
        return parse_for_predicate('is', instruc)

    first_brace = instruc.find('(')
    if first_brace != -1:
        predicate = instruc[:first_brace]

        if instruc[first_brace+1] == ')':
            return predicate, 0

        brace_balance = 1

        def count_args(entry_balance=brace_balance):
            args = 1
            pred_depth = entry_balance
            arr_depth = 0
            idx = first_brace+1
            while idx < len(instruc) and pred_depth > 0:
                if instruc[idx] == '(':
                    pred_depth += 1
                elif instruc[idx] == ')':
                    pred_depth -= 1
                elif instruc[idx] == '[':
                    arr_depth += 1
                elif instruc[idx] == ']':
                    arr_depth -= 1
                elif instruc[idx] == ',' and pred_depth == entry_balance and arr_depth == 0:
                    args += 1
                idx += 1

            return args

        args = count_args()
        return predicate, args
    return instruc, 0


def analyze_trace(lines: list):
    parsed_lines = []
    for line in lines:
        parsed_lines.append(preprocess_line(line))

    for i in range(len(parsed_lines)):
        _, depth, _ = parsed_lines[0]
        init_depth = depth
        if i == 0:
            print_with_indent(parsed_lines[i])
        else:
            _, last_depth, _ = parsed_lines[i-1]
            cur_todo, cur_depth, _ = parsed_lines[i]
            if cur_todo is None:
                continue
            if i < len(parsed_lines)-1:
                _, next_depth, _ = parsed_lines[i+1]
            else:
                next_depth = cur_depth
            indent = 2*(cur_depth-init_depth) * [' ']
            if cur_depth > last_depth:
                indent[-2:] = '\\_'
            elif cur_depth == last_depth or cur_todo == 'Exit' or cur_todo == 'Redo':
                print(' '*11, len(indent)*' ', '|', sep='')
            if cur_depth > next_depth and cur_todo == 'Exit':
                indent[-2*(cur_depth-next_depth):] = '_' * 2 * (cur_depth-next_depth)
                indent[-2*(cur_depth-next_depth)] = ' '
                indent[-1] = '/'

            print_with_indent(parsed_lines[i], indent)

            if cur_todo == 'Fail':
                print(' '*11, len(indent)*' ', '|', sep='')
                print(' '*11, len(indent)*' ', sep='', end='')
                color_print('X', bcolors.FAIL)


def print_with_indent(data, indent=()):
    todo, depth, instruc = data
    color = bcolors.OKGREEN
    if todo == 'Fail':
        color = bcolors.FAIL
    elif todo == 'Redo':
        color = bcolors.OKBLUE

    color_print(f'[{todo} {depth}]', color, end='  ')
    print(''.join(indent), sep='', end='')
    pred, _ = parse_instruction(instruc)
    pred_pos = instruc.find(pred)
    print(instruc[:pred_pos], end='')
    color_print(pred, bcolors.OKCYAN, end='')
    print(instruc[pred_pos+len(pred):])


def main():
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} path/to/source/file')
    source_file = sys.argv[1]
    trace_output = run_prolog(source_file)
    analyze_trace(trace_output.splitlines()[:-1])


if __name__ == '__main__':
    main()
