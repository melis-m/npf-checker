import elftools.elf.elffile
import requests
import urllib
import core.checks.base as base
import core.checks.utils as utils
import core.log as log


class ElfDepsChecker(base.CheckWithManifest):
    def __init__(self, pkg):
        super().__init__(
                pkg,
                filter(self._is_elf, utils.find_files('./usr/{,s}bin/**/*', './usr/lib{32,64}/**/*.so')),
        )

    def validate(self, item):
        log.i(f"Checking {item}")
        deps = self._fetch_elf_deps(item)
        for d in deps:
            results = self._solve_remotely(d)
        return True

    def show(self, item):
        pass

    def diff(self, item):
        pass

    def run(self):
        log.s("Looking for missing elf dependencies")
        super().run()

    @staticmethod
    def _solve_remotely(dependency):
        with log.push():
            results = {}
            repositories = ['stable', 'beta', 'unstable']
            endpoint = 'raven-os.org'
            for repository in repositories:
                url = f'https://{repository}.{endpoint}/api/search?q={urllib.parse.quote(dependency)}&search_by=content&exact_match=true'
                log.i(f"Looking on repository {repository}")
                try:
                    resp = requests.get(url)
                    if resp.ok:
                        current_results = resp.json()
                        results[repository] = list(map(lambda x: x['name'], current_results))
                    elif resp.status_code == 404:
                        results[repository] = []
                    else:
                        raise RuntimeError(f"Repository returned an unknown status code: {resp.status_code}")
                except Exception as e:
                    log.e(e)
                    log.e(f"An unknown error occurred when fetching \"{repository}\" (is the link dead?), skipping...")
        for rep, deps in results.items():
            log.d(f"{rep}: Found {deps or 'nothing'}")
        return results


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

