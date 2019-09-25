import core.args
import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.duplicate_files as dup
import core.checks.version_validity as version


def check_package(pkg):
    exe.ExecCheck().run()
    stx.DescriptionCheck(pkg).run()
    version.VersionValidityCheck(pkg).run()
    if core.args.get_args().no_skip_duplicate_files_check:
        dup.DuplicateFilesCheck(pkg).run()
