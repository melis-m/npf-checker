import sys
import toml
import core.args
import core.log as log

global _config


def load():
    global _config
    _config = toml.load(core.args.get_args().config)
    _check_file()


def _check_file():
    error = False
    for repo_name in _config['repositories']:
        repo = _config['repositories'][repo_name]
        if 'url' not in repo:
            log.e(f"A 'url' field is missing in Config.toml for repository '{repo_name}'")
            error = True
    if error:
        sys.exit(1)


def get():
    return _config
