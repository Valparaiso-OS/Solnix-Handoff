#!/usr/bin/env python3
"""Sign or verify a Solnix boot manifest with RSA-PSS-2048 and SHA-256."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

REQUIRED_FILES = (
    "boot/defaults/loader.conf",
    "boot/loader.conf",
    "boot/loader.rc",
    "platform/i86pc/amd64/boot_archive",
    "platform/i86pc/kernel/amd64/unix",
)
OPTIONAL_FILES = (
    "boot/loader.conf.local",
    "boot/menu.rc",
    "boot/loader.rc.local",
    "boot/menu.rc.local",
    "boot/solaris/bootenv.rc",
    "platform/i86pc/amd64/boot_archive.hash",
)
CONFIG_TREES = ("boot/conf.d", "boot/defaults", "boot/forth")
MANIFEST = "boot.manifest"
SIGNATURE = "boot.manifest.sig"
MANIFEST_LIMIT = 64 * 1024
SIGNATURE_BYTES = 256
MANIFEST_HEADER = "SOLNIX-BOOT-MANIFEST 1 SHA256 RSA-PSS-2048\n"
PSS_OPTIONS = ("-sigopt", "rsa_padding_mode:pss", "-sigopt", "rsa_pss_saltlen:digest")


def openssl(*args):
    return subprocess.run(
        [os.environ.get("SOLNIX_OPENSSL", "openssl"), *args],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def check_key(key, public):
    options = ["-pubin"] if public else []
    details = openssl("pkey", *options, "-in", key, "-text", "-noout").decode("ascii")
    if not re.search(r"(?:Public|Private)-Key: \(2048 bit(?:,|\))", details):
        raise ValueError("Expected an RSA-2048 key")


def regular_file(root, name):
    path = root
    for part in Path(name).parts[:-1]:
        path /= part
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError(f"Invalid boot directory {path}")
    path = root / name
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"Expected a regular boot file at {name}")
    return path


def tree_files(root, name):
    path = root / name
    if not stat.S_ISDIR(path.lstat().st_mode):
        raise ValueError(f"Invalid boot directory {name}")
    for entry in path.iterdir():
        relative = entry.relative_to(root).as_posix()
        if stat.S_ISDIR(entry.lstat().st_mode):
            yield from tree_files(root, relative)
        else:
            yield relative


def manifest_bytes(root):
    if not stat.S_ISDIR((root / "boot").lstat().st_mode):
        raise ValueError("Expected a real boot directory")
    names = set(REQUIRED_FILES)
    for name in OPTIONAL_FILES:
        path = root / name
        if path.exists() or path.is_symlink():
            names.add(name)
    for name in CONFIG_TREES:
        if (root / name).exists() or (root / name).is_symlink():
            for entry in tree_files(root, name):
                if name == "boot/conf.d" and (
                    Path(entry).parent.as_posix() != name or len(Path(entry).name) > 255
                ):
                    raise ValueError(f"Invalid boot configuration fragment {entry}")
                names.add(entry)

    lines = [MANIFEST_HEADER]
    for name in sorted(names):
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", name):
            raise ValueError(f"Invalid boot path {name!r}")
        digest = hashlib.sha256()
        with regular_file(root, name).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        lines.append(f"{digest.hexdigest()}  {name}\n")
    payload = "".join(lines).encode("ascii")
    if len(payload) > MANIFEST_LIMIT:
        raise ValueError("Boot manifest exceeds the EFI size limit")
    return payload


def sign(root, key, output):
    check_key(key, public=False)
    payload = manifest_bytes(root)
    with tempfile.TemporaryDirectory(prefix=".solnix-manifest-", dir=output.parent) as work:
        manifest = Path(work) / MANIFEST
        signature = Path(work) / SIGNATURE
        manifest.write_bytes(payload)
        openssl(
            "dgst", "-sha256", "-sign", key, *PSS_OPTIONS,
            "-out", signature, manifest,
        )
        if signature.stat().st_size != SIGNATURE_BYTES:
            raise ValueError("Unexpected RSA-2048 signature size")
        output.mkdir(mode=0o700)
        (output / MANIFEST).write_bytes(payload)
        (output / SIGNATURE).write_bytes(signature.read_bytes())


def verify(root, key, bundle):
    check_key(key, public=True)
    manifest = bundle / MANIFEST
    signature = bundle / SIGNATURE
    if signature.stat().st_size != SIGNATURE_BYTES:
        raise ValueError("Unexpected RSA-2048 signature size")
    if manifest.stat().st_size == 0 or manifest.stat().st_size > MANIFEST_LIMIT:
        raise ValueError("Invalid boot manifest size")
    expected = manifest_bytes(root)
    if manifest.read_bytes() != expected:
        raise ValueError("Signed manifest does not match the boot payload")
    with tempfile.TemporaryDirectory(prefix="solnix-manifest-check-") as work:
        candidate = Path(work) / MANIFEST
        candidate.write_bytes(expected)
        openssl(
            "dgst", "-sha256", "-verify", key, *PSS_OPTIONS,
            "-signature", signature, candidate,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("sign", "verify"))
    parser.add_argument("boot_root", type=Path)
    parser.add_argument("key", type=Path, help="private PEM for sign, trusted public PEM for verify")
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        action = sign if args.action == "sign" else verify
        action(args.boot_root, args.key, args.bundle)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"RSA-PSS-2048 boot manifest {args.action} succeeded")


if __name__ == "__main__":
    main()
