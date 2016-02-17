#!/usr/bin/python3
import os
import pathlib
import sys


def fix_object(path, base):
    try:
        st = path.lstat()
    except FileNotFoundError:
        # whatever
        return

    uid, gid = st.st_uid, st.st_gid
    change = False
    if not (0 <= uid-base <= 65535):
        change = True
        uid = (uid%100000) + base
    if not (0 <= gid-base <= 65535):
        change = True
        gid = (gid%100000) + base
    if change:
        os.lchown(str(path), uid, gid)


def recurse_and_fix(root, base):
    fix_object(root, base)
    for child in root.iterdir():
        fix_object(child, base)

        try:
            abs_child = child.resolve()
        except FileNotFoundError:
            continue

        if abs_child.is_dir():
            recurse_and_fix(abs_child, base)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
    )
    parser.add_argument(
        "base",
        type=int
    )

    args = parser.parse_args()

    root = pathlib.Path(args.root).absolute()
    os.chroot(str(root))
    recurse_and_fix(pathlib.Path("/"), args.base)
