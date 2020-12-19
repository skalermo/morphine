class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def color_print(text, color=bcolors.OKGREEN, sep=' ', end='\n'):
    print(f'{color}{text}{bcolors.ENDC}', sep=sep, end=end)


def color_sprint(text, color=bcolors.WARNING):
    return f'{color}{text}{bcolors.ENDC}'
