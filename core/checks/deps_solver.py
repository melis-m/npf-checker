import elftools.elf.elffile
import requests
import urllib.parse
import core.checks.base as base
import core.checks.utils as utils
import core.log as log
import core.repositories


class ElfDepsChecker(base.CheckWithManifest):
    def __init__(self, pkg):
        elf_files = filter(
                self._is_elf,
                utils.find_files(
                    './{,usr}/{,s}bin/**/*',
                    './{,usr}/lib{,32,64}/**/*.so'
                )
        )
        self.repositories = core.repositories.get_all()
        self.new_deps = {}
        self.missing_deps = {}
        self.already_solved = []
        super().__init__(pkg, elf_files)

    def validate(self, item):
        log.i(f"Checking {item}")
        self.missing_deps = {}
        self.new_deps = {}
        deps = self._fetch_elf_deps(item)
        ret = True
        with log.push():
            for d in deps:
                if d not in self.already_solved:
                    log.i(f"Checking {d}")
                    with log.push():
                        if not self._solve_in_repositories(d, self.repositories):
                            ret = False
                else:
                    log.i(f"Ignoring {d} because it has already been done")

        return ret

    def show(self, item):
        for file, pkgs in self.missing_deps.items():
            new = next(first['name'] for first in pkgs if first['all_versions'])
            if new not in self.new_deps:
                self.new_deps[new] = []
            self.new_deps[new].append(file)
        log.i("Some dependencies seem to be missing")

    def diff(self, item):
        log.i("The following dependencies would be added")
        with log.push():
            for dep, files in self.new_deps.items():
                log.i(f"{dep}#* (to satisfy {', '.join(files)})")

    def fix(self, item):
        for dep, _ in self.new_deps.items():
            self.pkg.manifest['dependencies'][dep] = '*'
        self.write_pkg_manifest()

    def run(self):
        log.s("Looking for missing elf dependencies")
        super().run()

    def _solve_in_repositories(self, dep, repos):
        self.already_solved.append(dep)
        for repo_name, repo in repos.items():
            res = self._solve_in_repository(dep, repo['url'])
            if res in self.pkg.manifest['dependencies']:
                del self.missing_deps[dep]
                return True
        return False

    def _solve_in_repository(self, dependency, repository_url):
        url = f'{repository_url}/api/search?q={urllib.parse.quote(dependency)}&search_by=content&exact_match=true'
        try:
            resp = requests.get(url)
            if resp.ok:
                current_results = resp.json()
                if current_results:
                    if dependency not in self.missing_deps:
                        self.missing_deps[dependency] = []
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
            log.i(f"Found deps to: {deps}")
        return deps

    @staticmethod
    def _is_elf(filename):
        try:
            with open(filename, 'rb') as f:
                elftools.elf.elffile.ELFFile(f)
        except Exception:
            return False
        return True
