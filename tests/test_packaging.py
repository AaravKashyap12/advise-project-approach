import os
import stat
import struct
from zipfile import ZipFile

from tests.support import AGENT, DIST, NAME, SKILL, RepositoryTestCase


class ArchiveTests(RepositoryTestCase):
    def test_members_must_match_source_payloads(self):
        entries = self.archive_entries()
        for payload in (b"wrong payload", b"", b"x" * len(entries[0][1])):
            with self.subTest(payload=payload):
                self.write_archive([(entries[0][0], payload), entries[1]])
                self.assert_invalid("package")

    def test_extra_missing_and_duplicate_entries(self):
        entries = self.archive_entries()
        for changed in (entries[:1], entries + [(f"{NAME}/extra.txt", b"extra")],
                        entries + [entries[0]], entries + [("unexpected/", b"")],
                        entries + [("../outside/", b"never extracted")]):
            with self.subTest(names=[name for name, _ in changed]):
                self.write_archive(changed)
                self.assert_invalid("package")

    def test_crc_corruption_is_read_and_rejected(self):
        with ZipFile(self.repo / DIST) as archive:
            offset = archive.infolist()[0].header_offset
        data = bytearray((self.repo / DIST).read_bytes())
        name_size, extra_size = struct.unpack_from("<HH", data, offset + 26)
        data[offset + 30 + name_size + extra_size] ^= 1
        (self.repo / DIST).write_bytes(data)
        self.assert_invalid("package")

    def test_bad_zip_reports_validation_error(self):
        (self.repo / DIST).write_bytes(b"not a zip")
        self.assert_invalid("package")

    def test_symlink_archive_member_is_rejected(self):
        with ZipFile(self.repo / DIST) as archive:
            entries = [(info, archive.read(info)) for info in archive.infolist()]
        entries[0][0].create_system = 3
        entries[0][0].external_attr = (stat.S_IFLNK | 0o644) << 16
        with ZipFile(self.repo / DIST, "w") as archive:
            for info, payload in entries:
                archive.writestr(info, payload)
        self.assert_invalid("package")

    def test_stale_archive_is_rejected(self):
        for relative in (SKILL, AGENT):
            with self.subTest(relative=relative):
                self.sync_archive()
                text = (self.repo / relative).read_text(encoding="utf-8")
                self.write(relative, text + "\n# changed source\n")
                self.assert_invalid("package")

    def test_crlf_payload_normalization(self):
        for relative in (SKILL, AGENT):
            data = (self.repo / relative).read_bytes()
            (self.repo / relative).write_bytes(data.replace(b"\n", b"\r\n"))
        self.assert_valid()


class PackagingTests(RepositoryTestCase):
    def test_reproducibility_and_minimal_archive(self):
        result = self.package()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = (self.repo / DIST).read_bytes()
        for relative in (SKILL, AGENT):
            path = self.repo / relative
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            os.utime(path, (1234567890, 1234567890))
        result = self.package()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.repo / DIST).read_bytes(), expected)
        with ZipFile(self.repo / DIST) as archive:
            self.assertEqual(set(archive.namelist()), {f"{NAME}/SKILL.md", f"{NAME}/agents/openai.yaml"})
            self.assertEqual(len(archive.infolist()), 2)
            self.assertIsNone(archive.testzip())
        self.assert_valid()

    def test_invalid_utf8_preserves_old_archive(self):
        before = (self.repo / DIST).read_bytes()
        (self.repo / AGENT).write_bytes(b"\xffinvalid UTF-8")
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual((self.repo / DIST).read_bytes(), before)
        self.assertEqual([p.name for p in (self.repo / "dist").iterdir()], [f"{NAME}.skill"])

    def test_write_failure_preserves_old_archive_and_removes_temporary_output(self):
        before = (self.repo / DIST).read_bytes()
        result = self.run_python("-c", "import runpy, sys; sys.path.insert(0, 'scripts'); from unittest.mock import patch; "
                                 "p = patch('zipfile.ZipFile.writestr', side_effect=OSError('injected write failure')); "
                                 "p.start(); runpy.run_path('scripts/package_skill.py', run_name='__main__')")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("injected write failure", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual((self.repo / DIST).read_bytes(), before)
        self.assertEqual([p.name for p in (self.repo / "dist").iterdir()], [f"{NAME}.skill"])

    def test_replace_failure_preserves_old_archive_and_removes_temporary_output(self):
        before = (self.repo / DIST).read_bytes()
        result = self.run_python("-c", "import runpy, sys; sys.path.insert(0, 'scripts'); from unittest.mock import patch; "
                                 "p = patch('os.replace', side_effect=OSError('injected replace failure')); "
                                 "p.start(); runpy.run_path('scripts/package_skill.py', run_name='__main__')")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("injected replace failure", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual((self.repo / DIST).read_bytes(), before)
        self.assertEqual([p.name for p in (self.repo / "dist").iterdir()], [f"{NAME}.skill"])

    def test_packager_rejects_extra_source_files(self):
        before = (self.repo / DIST).read_bytes()
        self.write(f"skills/{NAME}/unexpected.py", "# not runtime content\n")
        result = self.package()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.repo / DIST).read_bytes(), before)
