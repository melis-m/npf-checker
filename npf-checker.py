#!/usr/bin/env python3

import core.args
import core.config
import core.package
import core.log as log
import core.checks.base as base


def main():
    core.args.parse_args()
    core.config.load()

    args = core.args.get_args()
    base.Check.global_state = base.Type.from_string(core.args.get_args().action)
    f = args.npf
    pkg = core.package.Package(f)

    log.s(f"Unwrapping {f}")
    pkg.unwrap()
    log.s(f"Checking {f}")
    pkg.check()
    log.s(f"Wrapping {f}")
    pkg.wrap()


if __name__ == '__main__':
    main()
