"""Release versioning and artifact integrity tests; no device operations."""

import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "release_firmware", Path(__file__).resolve().parents[1] / "scripts/release_firmware.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def uf2(address=0x26000, family=0xADA52840):
    block = bytearray(512)
    struct.pack_into("<8I", block, 0, 0x0A324655, 0x9E5D5157, 0x2000,
                     address, 256, 0, 1, family)
    struct.pack_into("<I", block, 508, 0x0AB16F30)
    return bytes(block)


class ReleaseTests(unittest.TestCase):
    def test_first_release_and_patch_increment(self):
        self.assertEqual(release.select_tag({}, "a" * 40), "v0.1.0")
        self.assertEqual(release.select_tag({"v0.1.9": "b", "v0.1.10": "c"}, "a"), "v0.1.11")
        self.assertEqual(release.select_tag({"notes": "a", "v1.0.0-rc1": "a"}, "a"), "v0.1.0")

    def test_rerun_reuses_existing_commit_tag(self):
        self.assertEqual(release.select_tag({"v0.1.0": "a", "v0.1.1": "b"}, "a"), "v0.1.0")

    def test_rejects_bad_or_wrong_target_images(self):
        for data in (b"", b"bad", uf2(0xF4000), uf2(family=0x1234)):
            with self.subTest(data_size=len(data)), self.assertRaises(ValueError):
                release.validate_uf2(data)
        bad = bytearray(uf2())
        bad[-1] = 0
        with self.assertRaises(ValueError):
            release.validate_uf2(bytes(bad))

    def test_rejects_duplicate_blocks_and_wrong_sequence(self):
        with self.assertRaises(ValueError):
            release.validate_uf2(uf2() + uf2())
        duplicate = bytearray(uf2() + uf2())
        struct.pack_into("<I", duplicate, 24, 2)
        struct.pack_into("<I", duplicate, 512 + 20, 1)
        struct.pack_into("<I", duplicate, 512 + 24, 2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            release.validate_uf2(bytes(duplicate))
        bad = bytearray(uf2())
        struct.pack_into("<I", bad, 20, 1)
        with self.assertRaises(ValueError):
            release.validate_uf2(bytes(bad))

    def test_packages_all_three_images_with_matching_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source", root / "output"
            source.mkdir()
            for name in release.ASSETS:
                (source / name).write_bytes(uf2())
            release.package(source, output, "a" * 40, "v0.1.0", "owner/repo", "https://example.com/run")
            for line in (output / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ")
                self.assertEqual(digest, hashlib.sha256((output / name).read_bytes()).hexdigest())
            self.assertIn("clears saved settings", (output / "RELEASE_NOTES.md").read_text())

    def test_missing_asset_cannot_produce_a_partial_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                release.package(root, root / "output", "a" * 40, "v0.1.0", "owner/repo", "run")
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
