import core.config


def get_all():
    return core.config.get()['repositories']


def get_first_of(repos):
    for r_name, r in get_all().items():
        if r_name in repos:
            return r_name, r
    return None
