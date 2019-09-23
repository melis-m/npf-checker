import core.args
import core.config
import core.checks.base as base
import core.log as log


class DuplicateDepsCheck(base.CheckWithManifest):
    def __init__(self, pkg):
        self.pkgs_without_repo = self._gen_map_of_pkgs_to_repo(pkg)
        self.winning_repo = ""
        self.config_file_path = core.args.get_args().config
        super().__init__(pkg, self.pkgs_without_repo.items())

    @staticmethod
    def _gen_map_of_pkgs_to_repo(pkg):
        tuple_list = map(
            DuplicateDepsCheck._split_full_name,
            pkg.manifest['dependencies'],
        )
        d = {}
        [d[t[0]].append(t[1]) if t[0] in list(d.keys())
         else d.update({t[0]: [t[1]]}) for t in tuple_list]
        return d
        # This list comprehension transforms a list of tuples into a dict,
        # while handling duplicate keys,
        # See https://stackoverflow.com/a/51777132

    @staticmethod
    def _split_full_name(full_name):
        sep = full_name.find('::')
        return full_name[sep + 2:], full_name[:sep]

    def run(self):
        log.i("Checking for duplicate dependencies (e.g. same package but from different repos)")
        super().run()

    def validate(self, item):
        _, repos = item
        return len(repos) == 1

    def show(self, item):
        pkg, repos = item
        log.e(f"{pkg} is present more than once: {', '.join(repos)}")

    def diff(self, item):
        self.winning_repo = ""
        pkg, repos = item
        conf = core.config.get()
        lowest_idx = 0
        config_repos = list(conf['repositories'].keys())
        for repo in repos:
            try:
                idx = config_repos.index(repo)
                if idx < lowest_idx:
                    lowest_idx = idx
            except ValueError:
                log.w(f"Repository '{repo}' isn't defined in {self.config_file_path}, skipping...")
        self.winning_repo = config_repos[lowest_idx]
        log.i(
            f"The dependency to '{self.winning_repo}' will be kept, as it appears first in {self.config_file_path}")

    def fix(self, item):
        pkg, repos = item
        repos.remove(self.winning_repo)
        for repo in repos:
            del self.pkg.manifest['dependencies'][f'{repo}::{pkg}']
        self.write_pkg_manifest()
