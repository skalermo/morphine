import os
import subprocess

from morphine.colors import color_sprint, bcolors


class TraceFormatter:
    def __init__(self):
        self.prev_state = None
        self.init_depth = 0

    @staticmethod
    def check_if_prolog_trace(string):
        return string.startswith('^  ') or string.startswith('   ')

    def format_prolog_trace(self, string):
        cur_todo, cur_depth, cur_instruc = preprocess_line(string)

        if self.prev_state is None:
            self.init_depth = cur_depth
            formatted_line, indent_total = self.format_with_indent((cur_todo, cur_depth, cur_instruc,))
            before_line = ''
            after_line = self.connection_after_line(indent_total, cur_depth, cur_todo)
        else:
            cur_indent = self.match_indent(cur_todo, cur_depth)
            formatted_line, indent_total = self.format_with_indent((cur_todo, cur_depth, cur_instruc,), cur_indent)
            before_line = self.connection_before_line(indent_total, cur_depth)
            after_line = self.connection_after_line(indent_total, cur_depth, cur_todo)

        output = ''.join([before_line, formatted_line, after_line])
        self.prev_state = (cur_todo, cur_depth, cur_instruc,)
        return output

    def connection_before_line(self, indent_total, cur_depth):
        prev_todo, prev_depth, _ = self.prev_state
        if self.init_depth < cur_depth < prev_depth and prev_todo != 'Fail':
            if prev_depth - cur_depth == 1:
                return ''.join([' ' * (indent_total+1), '/\n', ' ' * indent_total, '|\n'])
            return ''.join([' ' * indent_total, ' ', '_' * 2 * (prev_depth - cur_depth-1), '/\n',
                            ' ' * indent_total, '|\n'])
        elif self.init_depth < cur_depth < prev_depth and prev_todo == 'Fail':
            return ''.join([' ' * indent_total, '|\n'])
        if cur_depth - prev_depth > 1:
            return ''.join([' ' * (indent_total-2*(cur_depth-prev_depth)), '\\', '_' * 2 * (cur_depth-prev_depth-2), '_\n'])
        return ''

    def connection_after_line(self, indent_total, cur_depth, cur_todo):
        if cur_depth < self.init_depth:
            return ''
        if cur_todo == 'Fail':
            return ''.join([' ' * indent_total, color_sprint('|', bcolors.FAIL), '\n',
                            ' ' * indent_total, color_sprint('X', bcolors.FAIL), '\n'])
        return ' ' * indent_total + '|\n'

    def format_with_indent(self, data, indent=''):
        todo, depth, instruc = data
        todo_color = {
            'Call': bcolors.OKGREEN,
            'Exit': bcolors.OKGREEN,
            'Redo': bcolors.OKBLUE,
            'Fail': bcolors.FAIL
        }.get(todo, bcolors.WARNING)
        info = f'[{todo} {depth}]'
        separator = ' ' * 2
        instruc = self.format_instruction(instruc)
        return ''.join([color_sprint(info, todo_color), separator, indent, instruc]), \
               len(info) + len(separator) + len(indent)

    @staticmethod
    def format_instruction(instruc):
        pred, _ = parse_instruction(instruc)
        pred_pos = instruc.find(pred)
        before_pred = instruc[:pred_pos]
        after_pred = instruc[pred_pos + len(pred):]
        return ''.join([before_pred, color_sprint(pred, bcolors.OKCYAN), after_pred])

    def match_indent(self, cur_todo, cur_depth):
        prev_todo, prev_depth, _ = self.prev_state
        indent = [' '] * 2 * (cur_depth - self.init_depth)
        if cur_depth > prev_depth:
            indent[-2:] = '\\_'
        return ''.join(indent)


def run_prolog(source_file):
    path = os.path.abspath(source_file)
    command = f'swipl -s {path} -g "leash(-all),trace,start." -t halt'
    print(command)
    result = subprocess.run([c.strip('"') for c in command.split()], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return result.stdout.decode('utf-8')


def preprocess_line(line: str):
    if line.startswith('ERROR'):
        return 'ERROR', -1, line[7:]
    if not (line.startswith('^  ') or line.startswith('   ')):
        return None
    split = line[3:].split(maxsplit=2)
    # if len(split) != 3:
    #     print(split)
    #     return None, 0, ''
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

        if instruc[first_brace + 1] == ')':
            return predicate, 0

        brace_balance = 1

        def count_args(entry_balance=brace_balance):
            args = 1
            pred_depth = entry_balance
            arr_depth = 0
            idx = first_brace + 1
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
