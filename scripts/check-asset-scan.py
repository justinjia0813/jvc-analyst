#!/usr/bin/env python3
"""Check the asset scanner's clean, rejected, and failed-read paths in a temp repo."""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = (ROOT / "scripts/check-jvc-assets.sh").read_text(encoding="utf-8")
    function = "reject_backticked_legacy_slash_commands() {" + source.split(
        "reject_backticked_legacy_slash_commands() {", 1
    )[1].split("\n}", 1)[0] + "\n}"
    command = "set -euo pipefail\n" + function + "\nreject_backticked_legacy_slash_commands"
    with TemporaryDirectory(prefix="jvc-asset-scan-") as temporary:
        root = Path(temporary)

        def scan() -> int:
            return subprocess.run(["bash", "-c", command], cwd=root,
                                  capture_output=True, check=False).returncode

        assert scan() != 0, "non-repository scan reported success"
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        document = root / "含 空格\n及换行.md"
        document.write_text("`/jvc-bull-case`\n", encoding="utf-8")
        assert scan() == 0, "valid command rejected"
        document.write_text("`/" + "bull-case`\n", encoding="utf-8")
        assert scan() != 0, "legacy command was silently accepted"
        document.write_text("valid\n", encoding="utf-8")
        (root / "missing.md").symlink_to(root / "absent-target")
        assert scan() != 0, "unreadable document reported success"
    print("asset scanner regression passed")


if __name__ == "__main__":
    main()
