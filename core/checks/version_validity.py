import core.log as log
import core.checks.base as base
import semver


class VersionValidityCheck(base.CheckWithManifest):
    def __init__(self, pkg):
        super().__init__(pkg, [pkg.manifest['version']])

    def validate(self, version):
        try:
            semver.valid(version, loose=False)
            return True
        except AttributeError:
            return False

    def show(self, version):
        log.e(f"The version isn't semver compliant")

    def diff(self, version):
        log.w("No fix can be done automatically")
        return False

    def fix(self, version):
        log.w("No fix can be done automatically")

    def run(self):
        log.s("Checking package version")
        super().run()
