import elftools.elf.elffile
import requests
import urllib
import core.checks.base as base
import core.checks.utils as utils
import core.log as log


class SingleElfDepChecker(base.CheckWithManifest):
    def __init__(self, pkg, dep_list, file_needed, by):
        super().__init__(pkg, [dep_list])
        self.file_needed = file_needed
        self.by = by

    def validate(self, dep_list):
        for dep in dep_list:
            if dep in self.manifest['dependencies']:
                return True
        return False

    def show(self, dep_list):
        log.i(f"No package dependency was found in manifest.toml to satisfy dependency to {self.file_needed} (required at least by {self.by})")

    def diff(self, dep_list):
        log.i(f"Dependency to {dep_list[0]} would be added, with '*' as version requirement")

    def fix(self, dep_list):
        self.manifest['dependencies'][dep_list[0]] = '*'
        self.write_pkg_manifest()


class ElfDepsChecker(base.CheckWithManifest):
    def __init__(self, pkg):
        elf_files = filter(
                self._is_elf,
                utils.find_files(
                    './{,usr}/{,s}bin/**/*',
                    './{,usr}/lib{,32,64}/**/*.so'
                )
        )
        self.missing_deps = {}
        self.already_solved = []
        super().__init__(pkg, elf_files)

    def validate(self, item):
        log.i(f"Checking {item}")
        self.missing_deps = {}
        deps = self._fetch_elf_deps(item)
        for d in deps:
            if d not in self.already_solved:
                repositories = map(
                        lambda x: f"{x}.raven-os.org",
                        ['stable', 'beta', 'unstable']
                )
                for rep in repositories:
                    res = self._solve_in_repository(d, rep)
                    self.already_solved.append(d)
                    if res in self.pkg.manifest['dependencies']:
                        return True
                    else:
                        return False
            else:
                log.i(f"Ignoring {d} because it has already been done")
        return True

    def show(self, item):
        log.d("show")
        log.d(item)
        log.d(f"missing deps: {self.missing_deps}")
        log.d(f"already solved:{self.already_solved}")

    def diff(self, item):
        log.d("diff")

    def fix(self, item):
        log.d("fix")

    def run(self):
        log.s("Looking for missing elf dependencies")
        super().run()

    def _solve_in_repository(self, dependency, repository_url):
        log.i(f"Looking in repository {repository_url}")
        url = f'https://{repository_url}/api/search?q={urllib.parse.quote(dependency)}&search_by=content&exact_match=true'
        try:
            resp = requests.get(url)
            if resp.ok:
                current_results = resp.json()
                if current_results:
                    if dependency not in self.missing_deps:
                        self.missing_deps[dependency] = []
                        return current_results
                    self.missing_deps[dependency] += current_results
                if len(current_results) == 1:
                    r = current_results[0]
                    if r['all_versions']:
                        return r['name']
                else:
                    return None
            elif resp.status_code == 404:
                return None
            else:
                raise RuntimeError(f"Repository returned an unknown status code: {resp.status_code}")
        except Exception as e:
            log.e(e)
            log.e(f"An unknown error occurred when fetching \"{repository_url}\" (is the link dead?), skipping...")

    @staticmethod
    def _fetch_elf_deps(filename):
        deps = []
        with open(filename, 'rb') as f, log.push():
            elf = elftools.elf.elffile.ELFFile(f)
            dyn = elf.get_section_by_name(".dynamic")
            if dyn is not None:
                for tag in dyn.iter_tags():
                    if tag.entry.d_tag == 'DT_NEEDED':
                        if tag.needed not in deps:
                            deps.append(tag.needed)
            log.d(f"Found deps: {deps}")
        return deps

    @staticmethod
    def _is_elf(filename):
        try:
            with open(filename, 'rb') as f:
                elftools.elf.elffile.ELFFile(f)
        except Exception:
            return False
        return True
