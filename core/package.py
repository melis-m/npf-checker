import shutil
import os
import tarfile
import toml
import datetime
import termcolor
import core
import core.log as log
import core.check


class Package:
    def __init__(self, npf_path):
        self.cache = core.args.get_args().cache_dir
        self.npf_path = npf_path
        self.is_effective = False

    def unwrap(self):
        if os.path.exists(self.cache):
            shutil.rmtree(self.cache)
        os.makedirs(self.cache)
        with tarfile.open(self.npf_path, 'r') as tar:
            tar.extractall(self.cache)
        self.manifest_path = os.path.join(self.cache, 'manifest.toml')
        self.manifest = toml.load(self.manifest_path)
        self.is_effective = self.manifest['kind'] == 'effective'
        data = os.path.join(self.cache, 'data.tar.gz')
        if os.path.exists(data):
            with tarfile.open(data, 'r:gz') as tar:
                tar.extractall(self.cache)
            os.remove(data)

    def check(self):
        core.check.check_package(self)

    def wrap(self):
        self.update_manifest_toml_wrap_date()
        self.show_manifest()
        if self.is_effective:
            self.create_data_tar()
        self.create_nest_file()

    def update_manifest_toml_wrap_date(self):
        self.manifest['wrap_date'] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        with open(self.manifest_path, 'w') as filename:
            toml.dump(self.manifest, filename)

    def create_data_tar(self):
        with core.pushd(self.cache):
            self.manifest = toml.load('manifest.toml')
            os.remove('manifest.toml')
            files_count = 0
            log.s("Files added:")
            with log.push():
                for root, _, filenames in os.walk('.'):
                    for name in filenames:
                        log.s(_colored_path(os.path.join(root, name)))
                        files_count += 1
            log.s(f"(That's {files_count} files.)")
            log.s(f"Creating data.tar.gz")
            with tarfile.open('data.tar.gz', 'w:gz') as archive:
                archive.add('./')
            with open('manifest.toml', 'w') as filename:
                toml.dump(self.manifest, filename)

    def create_nest_file(self):
        with core.pushd(self.cache):
            new_nest_file_path = os.path.basename(self.npf_path) + '.new'
            with tarfile.open(new_nest_file_path, 'w') as nest_file:
                nest_file.add('manifest.toml')
                if self.is_effective:
                    nest_file.add('data.tar.gz')
            os.remove('manifest.toml')
            if self.is_effective:
                os.remove('data.tar.gz')
        new_path = f'{self.npf_path}.new'
        os.rename(os.path.join(self.cache, new_nest_file_path), new_path)

    def show_manifest(self):
        m = self.manifest
        metadata = m['metadata']
        log.s(f"Manifest:")
        with log.push():
            log.s(f"name: {m['name']}")
            log.s(f"category: {m['category']}")
            log.s(f"version: {m['version']}")
            log.s(f"description: {metadata['description']}")
            log.s(f"tags: {', '.join(metadata['tags'])}")
            log.s(f"maintainer: {metadata['maintainer']}")
            log.s(f"licenses: {', '.join(metadata['licenses'])}")
            log.s(f"upstream_url: {metadata['upstream_url']}")
            log.s(f"kind: {m['kind']}")
            log.s(f"wrap_date: {datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'}")
            log.s(f"dependencies:")
            with log.push():
                for (full_name, version_req) in m['dependencies'].items():
                    log.s(f"{full_name}#{version_req}")


def _colored_path(path, pretty_path=None):
    if pretty_path is None:
        pretty_path = path

    if os.path.islink(path):
        target_path = os.path.join(
            os.path.dirname(path),
            os.readlink(path),
        )
        if os.path.exists(target_path):
            return f"{termcolor.colored(path, 'cyan', attrs=['bold'])} -> {_colored_path(target_path, os.readlink(path))}"
        else:
            return f"{termcolor.colored(path, on_color='on_red', attrs=['bold'])} -> {termcolor.colored(os.readlink(path), on_color='on_red', attrs=['bold'])}"
    elif os.path.isdir(path):
        return termcolor.colored(pretty_path, 'blue', attrs=['bold'])
    elif os.access(path, os.X_OK):
        return termcolor.colored(pretty_path, 'green', attrs=['bold'])
    else:
        return pretty_path
