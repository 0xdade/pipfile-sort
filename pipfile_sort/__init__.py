import argparse
import os

from plette import Pipfile
from plette.pipfiles import PackageCollection

VERSION = "0.2.1"
DESC = "Automatically alphabetize Pipfile dependencies"
PIPFILE_ENCODING = "utf-8"


def _parse_args():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit code reflects how many files were changed",
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)
    parser.add_argument(
        "--files",
        metavar="FILE",
        type=str,
        default=["./Pipfile"],
        nargs="+",
        help="Pipfile(s) to sort",
    )
    return parser.parse_args()


def _sort_collection(collection: PackageCollection):
    packages = [p for p in collection]
    sorted_packages = sorted(packages)

    return (
        PackageCollection({p: collection[p]._data for p in sorted_packages}),
        packages != sorted_packages,
    )


def _sort_pipfile(pipfile_name: str) -> bool:
    with open(pipfile_name, encoding=PIPFILE_ENCODING) as f:
        pipfile = Pipfile.load(f)

    sorted_dev_packages, dev_changed = _sort_collection(pipfile.dev_packages)
    sorted_packages, changed = _sort_collection(pipfile.packages)

    if dev_changed or changed:
        pipfile.dev_packages = sorted_dev_packages
        pipfile.packages = sorted_packages

        with open(pipfile_name, "w", encoding=PIPFILE_ENCODING) as f:
            Pipfile.dump(pipfile, f)

    return changed or dev_changed


def main():
    args = _parse_args()
    changes = []
    for pfile in args.files:
        if not os.path.isfile(pfile):
            pass
        changes.append(_sort_pipfile(pfile))

    if any(changes):
        print(f"{sum(changes)} file(s) changed")
        if args.exit_code:
            raise SystemExit(sum(changes))


if __name__ == "__main__":
    main()
