#!/usr/bin/env python3
"""Validate UF2 build artifacts and select repeatable GitHub Release versions."""

import argparse
import hashlib
from pathlib import Path
import re
import struct
import subprocess


ASSETS = ("eyelash-sofle-left.uf2", "eyelash-sofle-right.uf2", "settings-reset.uf2")
VERSION = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
COMMIT = re.compile(r"[0-9a-f]{40}")


def select_tag(tags: dict[str, str], commit: str) -> str:
    versions = {
        tag: tuple(map(int, match.groups()))
        for tag in tags
        if (match := VERSION.fullmatch(tag))
    }
    matching = [tag for tag in versions if tags[tag] == commit]
    if matching:
        return max(matching, key=versions.__getitem__)
    if not versions:
        return "v0.1.0"
    major, minor, patch = max(versions.values())
    return f"v{major}.{minor}.{patch + 1}"


def repository_tags() -> dict[str, str]:
    names = subprocess.check_output(["git", "tag", "--list"], text=True).splitlines()
    return {
        tag: subprocess.check_output(["git", "rev-parse", f"{tag}^{{commit}}"], text=True).strip()
        for tag in names
        if VERSION.fullmatch(tag)
    }


def validate_uf2(data: bytes) -> None:
    if not data or len(data) % 512:
        raise ValueError("UF2 must contain complete 512-byte blocks")
    blocks = len(data) // 512
    addresses: set[int] = set()
    for number in range(blocks):
        offset = number * 512
        magic0, magic1, flags, address, size, index, total, family = struct.unpack_from(
            "<8I", data, offset
        )
        if (magic0, magic1) != (0x0A324655, 0x9E5D5157):
            raise ValueError("Invalid UF2 block header")
        if struct.unpack_from("<I", data, offset + 508)[0] != 0x0AB16F30:
            raise ValueError("Invalid UF2 block trailer")
        if flags != 0x2000 or family != 0xADA52840:
            raise ValueError("UF2 is not an nRF52840 application image")
        if size != 256 or index != number or total != blocks:
            raise ValueError("Invalid UF2 payload size or block sequence")
        if address % 256 or not 0x26000 <= address < address + size <= 0xEC000:
            raise ValueError("UF2 would write outside the application's flash region")
        if address in addresses:
            raise ValueError("UF2 contains duplicate flash addresses")
        addresses.add(address)


def package(source: Path, destination: Path, commit: str, tag: str, repository: str,
            run_url: str) -> None:
    if not COMMIT.fullmatch(commit) or not VERSION.fullmatch(tag):
        raise ValueError("A full commit SHA and semantic version tag are required")
    # Validate every image before writing release output.
    images = {name: (source / name).read_bytes() for name in ASSETS}
    for name, data in images.items():
        try:
            validate_uf2(data)
        except ValueError as error:
            raise ValueError(f"{name}: {error}") from error
    destination.mkdir(parents=True, exist_ok=True)
    for name in ASSETS:
        (destination / name).write_bytes(images[name])
    checksums = "".join(
        f"{hashlib.sha256(images[name]).hexdigest()}  {name}\n" for name in sorted(ASSETS)
    )
    (destination / "SHA256SUMS").write_text(checksums)
    (destination / "RELEASE_NOTES.md").write_text(
        f"Firmware built from [{commit[:7]}](https://github.com/{repository}/commit/{commit}).\n\n"
        "Includes Studio-remappable clockwise/counterclockwise encoder keys and removal "
        "of the Q/S/Z shutdown shortcut.\n\n"
        "- `eyelash-sofle-left.uf2`: left/central half, including ZMK Studio.\n"
        "- `eyelash-sofle-right.uf2`: right/peripheral half.\n"
        "- `settings-reset.uf2`: recovery image that clears saved settings and pairing. "
        "Use the left/right images for normal updates.\n"
        "- `SHA256SUMS`: SHA-256 checksums for all three images.\n\n"
        "Flash each image to its matching half over USB. In Studio, the two keys below "
        "the left thumb keys control counterclockwise (left) and clockwise (right) "
        "rotation; their defaults are volume down/up.\n\n"
        f"[Build and test results]({run_url}).\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    version = commands.add_parser("tag")
    version.add_argument("--commit", required=True)
    assets = commands.add_parser("package")
    assets.add_argument("--input", type=Path, required=True)
    assets.add_argument("--output", type=Path, required=True)
    for option in ("commit", "tag", "repository", "run-url"):
        assets.add_argument(f"--{option}", required=True)
    args = parser.parse_args()
    if args.command == "tag":
        if not COMMIT.fullmatch(args.commit):
            parser.error("--commit must be a full commit SHA")
        print(select_tag(repository_tags(), args.commit))
    else:
        package(args.input, args.output, args.commit, args.tag, args.repository, args.run_url)


if __name__ == "__main__":
    main()
