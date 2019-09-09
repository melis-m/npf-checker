import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.duplicate_files as dup


def check_package(pkg):
    exe.ExecCheck().run()
    stx.DescriptionCheck(pkg).run()
    dup.DuplicateFilesCheck(pkg).run()
