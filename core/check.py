import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.duplicate_files as dup
import core.checks.version_validity as version


def check_package(pkg):
    exe.ExecCheck().run()
    stx.DescriptionCheck(pkg).run()
    dup.DuplicateFilesCheck(pkg).run()
    version.VersionValidityCheck(pkg).run()
