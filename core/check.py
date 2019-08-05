import core.checks.executable as exe
import core.checks.syntax_check as stx
import core.checks.version_reqs_resolvability as verreqsolv
import core.checks.deps_solver as deps_solver


def check_package(pkg):
    # exe.ExecCheck().run()
    # stx.DescriptionCheck(pkg).run()
    # verreqsolv.VersionReqsResolvabilityCheck(pkg).run()
    deps_solver.ElfDepsChecker(pkg).run()
