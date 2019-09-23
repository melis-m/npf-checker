import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.version_reqs_resolvability as verreqsolv
import core.checks.deps_solver as deps_solver
import core.checks.version_validity as version


def check_package(pkg):
    # exe.ExecCheck().run()
    # stx.DescriptionCheck(pkg).run()
    # verreqsolv.VersionReqsResolvabilityCheck(pkg).run()
    # version.VersionValidityCheck(pkg).run()
    deps_solver.ElfDepsChecker(pkg).run()
