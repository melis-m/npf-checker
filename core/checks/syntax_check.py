import core.log as log
import core.checks.base as base


class DescriptionCheck(base.CheckWithManifest):
    def __init__(self, pkg):
        super().__init__(pkg, None)  # items is provided on the next line
        self.items = [pkg.manifest['metadata']['description']]
        self.capital = False
        self.full_stop = False

    def validate(self, description):
        self.capital = description[0].isupper()
        self.full_stop = description[-1] == '.'
        return len(description) >= 2 and self.capital and self.full_stop

    def show(self, description):
        log.e(
            f"The description of the package doesn't respect the required syntax"
        )

    def fix(self, description):
        if len(description) < 2:
            log.w("Nothing can be done automatically, the description is too short")
        else:
            if not self.full_stop:
                description += '.'
                log.i("Full stop has been added at the end")
            if not self.capital:
                description = description[0].upper() + description[1:]
                log.i("First letter has been converted to uppercase")
            self.pkg.manifest['metadata']['description'] = description
            self.write_pkg_manifest()

    def diff(self, description):
        if not self.capital:
            log.i("The first letter would be converted to uppercase")
        if not self.full_stop:
            log.i("A full stop would be added at the end")

    def run(self):
        log.s("Checking the description of the package")
        super().run()
