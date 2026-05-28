#!/usr/bin/env python3
"""Build the distributable .skill archive."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "advise-project-approach"
SOURCE_DIR = ROOT / "skills" / SKILL_NAME
DIST_DIR = ROOT / "dist"
OUT_FILE = DIST_DIR / f"{SKILL_NAME}.skill"


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"Missing skill source: {SOURCE_DIR}")

    DIST_DIR.mkdir(exist_ok=True)
    if OUT_FILE.exists():
        OUT_FILE.unlink()

    with ZipFile(OUT_FILE, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE_DIR.rglob("*")):
            if path.is_file():
                relative = path.relative_to(SOURCE_DIR.parent)
                info = ZipInfo(relative.as_posix())
                info.date_time = (2026, 1, 1, 0, 0, 0)
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())

    print(f"Built {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
