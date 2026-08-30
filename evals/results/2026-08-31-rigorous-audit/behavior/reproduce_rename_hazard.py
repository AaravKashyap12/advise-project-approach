"""Counterexample to the recommended plan-then-os.replace operation, not an app test."""

import hashlib
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="apa-rename-counterexample-") as scratch:
    source = Path(scratch) / "original.jpg"
    target = Path(scratch) / "20260831.jpg"
    source.write_bytes(b"SYNTHETIC_PHOTO_A")
    plan_target_absent = not target.exists()
    target.write_bytes(b"SYNTHETIC_UNRELATED_PHOTO_B_CREATED_AFTER_PLAN")
    before = hashlib.sha256(target.read_bytes()).hexdigest()
    os.replace(source, target)
    after = hashlib.sha256(target.read_bytes()).hexdigest()
    evidence = {
        "scenario": "A destination is created after a clean dry-run plan but before apply.",
        "suggested_primitive": "os.replace(source, target)",
        "plan_marked_no_collision": plan_target_absent,
        "unrelated_destination_sha256_before": before,
        "destination_sha256_after": after,
        "unrelated_destination_preserved": before == after,
        "source_exists_after": source.exists(),
        "scope": "Disposable synthetic bytes only. This demonstrates an omitted safety condition in both holdout treatment answers, not a bug in any real user application.",
    }
    assert plan_target_absent and before != after and not source.exists()
(HERE / "rename-counterexample.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
print(json.dumps(evidence, indent=2))
