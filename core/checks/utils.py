import enum
import os
import braceexpand
import glob
import core.log as log
import core.args


class Answer(enum.Enum):
    YES = enum.auto()
    NO = enum.auto()
    EDIT = enum.auto()
    NONE = enum.auto()


def ask_yne(question, default=Answer.YES):
    while True:
        s = ""
        if default == Answer.YES:
            s = 'Y/n/e'
        elif default == Answer.NO:
            s = 'y/N/e'
        elif default == Answer.EDIT:
            s = 'y/n/E'
        answer = log.q(f"{question} [{s}] ").lower()
        if answer == '':
            return default
        elif answer in ['y', 'yes', 'ye']:
            return Answer.YES
        elif answer in ['n', 'no']:
            return Answer.NO
        elif answer in ['e', 'edit']:
            return Answer.EDIT
        else:
            log.w("Unrecognized answer")
            continue


def ask_yn(question, default=True):
    while True:
        s = '[Y/n]' if default else ['y/N']
        answer = log.q(f"{question} {s} ").lower()
        if answer == '':
            return default
        elif answer in ['y', 'yes', 'ye']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            log.w("Unrecognized answer")
            continue


def open_shell(path):
    args = core.args.get_args()
    if args.visual:
        ret = os.system(f'xdg-open {path}')
        if ret == 0:
            return
        else:
            log.w("A problem occured while using xdg-open, falling back on opening a shell")
    shell = os.environ.get('SHELL')
    if shell is None:
        log.w("No $SHELL environment variable found")
        shell = log.q("Please provide a valid shell: ")
    log.i(f"Opening {shell} in {path}, press CTRL-D to exit and resume checks")
    os.system(f'cd {path} && {shell}')


def open_editor(filepath):
    args = core.args.get_args()
    if args.visual:
        editor = os.environ.get('VISUAL')
        if editor is None:
            log.w("No $VISUAL environment variable found, trying $EDITOR")
            editor = os.environ.get('EDITOR')
            if editor is None:
                log.w("No $EDITOR environment variable found")
                editor = log.q("Please provide a valid editor: ")
    else:
        editor = os.environ.get('EDITOR')
        if editor is None:
            log.w("No $EDITOR environment variable found")
            editor = log.q("Please provide a valid editor: ")
    log.i(f"Opening {filepath} with {editor}")
    os.system(f'{editor} {filepath}')


def find_files(*paths):
    files = []
    cache = core.args.get_args().cache_dir
    with core.pushd(cache):
        for path in paths:
            for rglob in braceexpand.braceexpand(path):
                if os.path.isabs(rglob):
                    raise RuntimeError(f"Cannot receive absolute path '{rglob}'")
                for rpath in glob.glob(rglob, recursive=True):
                    files.append(rpath)
    return files
