import os
import stat
import core.log as log
import core.checks.base as base
import core.checks.utils as utils


class FilesExecCheck(base.Check):
    def __init__(self, files):
        super().__init__(files)

    def validate(self, item):
        log.i(f"Checking {item}")
        return os.access(item, os.X_OK)

    def show(self, item):
        log.e(f"'{item}' is not executable, but should be")

    def fix(self, item):
        perms = os.stat(item).st_mode
        log.i(f"'{item}' has been given execute permissions")
        os.chmod(item, perms | stat.S_IXOTH | stat.S_IXGRP | stat.S_IXUSR)

    def diff(self, item):
        log.i("X permissions would be added")

    def edit(self, item):
        utils.open_shell(os.path.dirname(item))


class ExecCheck():
    def run(self):
        log.s(f"Checking files execute permission")
        FilesExecCheck(utils.find_files('./{,usr}/{,s}bin/**/*')).run()
        FilesExecCheck(utils.find_files('./{,usr}/lib{,32,64}/**/*.so')).run()
