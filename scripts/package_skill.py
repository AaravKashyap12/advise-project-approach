#!/usr/bin/env python3
"""Build the distributable .skill archive."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from validate_skill import read_text, validate_source


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "advise-project-approach"
SOURCE_DIR = ROOT / "skills" / SKILL_NAME
DIST_DIR = ROOT / "dist"
OUT_FILE = DIST_DIR / f"{SKILL_NAME}.skill"


def main() -> None:
    validate_source()
    paths = sorted(
        (path for path in SOURCE_DIR.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(SOURCE_DIR.parent).as_posix().lower(),
    )

    payloads = [(path.relative_to(SOURCE_DIR.parent).as_posix(), read_text(path).encode("utf-8"))
                for path in paths]
    temporary = None
    try:
        DIST_DIR.mkdir(exist_ok=True)
        with NamedTemporaryFile(dir=DIST_DIR, prefix=f".{SKILL_NAME}.", suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
                for relative, data in payloads:
                    info = ZipInfo(relative)
                    info.date_time = (2026, 1, 1, 0, 0, 0)
                    info.compress_type = ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o644 << 16
                    archive.writestr(info, data)
        temporary.chmod(0o644)
        # The final path changes only after a complete ZIP has been closed.
        temporary.replace(OUT_FILE)
    except OSError as exc:
        raise SystemExit(f"Packaging failed: {exc}") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    print(f"Built {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
