import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.version_validity as version
import core.checks.duplicate_deps as dup_deps


def check_package(pkg):
    # exe.ExecCheck().run()
    # stx.DescriptionCheck(pkg).run()
    # version.VersionValidityCheck(pkg).run()
    dup_deps.DuplicateDepsCheck(pkg).run()
