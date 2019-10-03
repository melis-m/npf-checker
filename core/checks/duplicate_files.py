import requests
import os.path
import core.checks.base as base
import core.log as log
import core.checks.utils as utils
import core.repositories


class DuplicateFilesCheck(base.Check):
    def __init__(self, pkg):
        super().__init__(
            filter(
                lambda x: x != 'manifest.toml' and not os.path.isdir(x),
                utils.find_files_generator('**/*'),
            ),
        )
        self.match = []
        self.pkg = pkg
        self.repositories = core.repositories.get_all()

    def run(self):
        log.s("Checking if the new files are not already in other packages")
        super().run()
        
    def validate(self, item):
        log.i(f"Checking {item}")
        self.match = []
        with log.push():
            for repo in self.repositories.items():
                self.check_in_repo(item, repo)

    def check_in_repo(self, item, repo):
        repo_name, repo_data = repo
        repo_url = repo_data['url']
        log.i(f"On repository {repo_name} ({repo_url})")
        try:
            resp = requests.get(
                url=f'{repo_url}/api/search',
                params={
                    'q': os.path.basename(item),
                    'search_by': 'content',
                    'exact_match': 'true'
                }
            )
            if resp.ok:
                for res in resp.json():
                    if res['path'] == f'/{item}':
                        repo, cat_name = res['name'].split('::')
                        m = self.pkg.manifest
                        if cat_name != f'{m["category"]}/{m["name"]}':
                            self.match.append(res['name'])
                            return False
                return True
            else:
                log.e(resp.content)
                log.e(
                    f"An unknown error occurred when fetching \"{repo_url}\" (is the link dead?), skipping...")
                return True
        except Exception as e:
            log.e(e)
            log.e(
                f"An unknown error occurred when fetching \"{repo_url}\" (is the link dead?), skipping...")
            return True

    def show(self, item):
        log.w(f"{item} is already present in {', '.join(self.match)}")

    def diff(self, item):
        log.i(f"{item} would be removed from the package")

    def fix(self, item):
        os.remove(item)
        log.i(f"{item} has been removed")

    def edit(self, item):
        utils.open_shell(os.path.dirname(item))
