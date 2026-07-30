#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
USER_SKILLS = {
    "jvc-prescreen",
    "jvc-bull-case",
    "jvc-track-research",
    "jvc-research-report",
    "jvc-knowledge-tree-builder",
    "jvc-comps-dd",
    "jvc-market-sizing",
    "jvc-roi-modeler",
    "jvc-bear-case",
    "jvc-ic-memo",
    "jvc-meeting-notes",
    "jvc-talk-notes",
    "jvc-invoice-manager",
}
COMPONENT_COUNT = len(USER_SKILLS) + 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def copy_package(destination: Path) -> None:
    destination.mkdir()
    shutil.copy2(ROOT / "setup", destination / "setup")
    shutil.copytree(ROOT / "skills", destination / "skills")


def clean_env(home: Path, ceiling: Path, base: Mapping[str, str]) -> dict[str, str]:
    env = {key: value for key, value in base.items() if not key.startswith("GIT_")}
    env.update({"HOME": str(home), "GIT_CEILING_DIRECTORIES": str(ceiling)})
    return env


def run_setup(
    package: Path,
    home: Path,
    ceiling: Path,
    base_env: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    env = clean_env(home, ceiling, base_env)
    git_keys = {key for key in env if key.startswith("GIT_")}
    require(
        git_keys == {"GIT_CEILING_DIRECTORIES"},
        f"Git variables leaked into install environment: {sorted(git_keys)}",
    )
    return subprocess.run(
        ["bash", str(package / "setup")],
        cwd=package,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def tree_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def main() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        package = root / "jvc-analyst"
        home = root / "home"
        sentinel = root / "git-sentinel"
        (home / ".codex" / "skills" / "jvc-prescreen").mkdir(parents=True)
        customization = home / ".codex" / "skills" / "jvc-prescreen" / "user-customization.txt"
        customization.write_text("keep me\n", encoding="utf-8")
        (sentinel / ".agents").mkdir(parents=True)
        sentinel_marker = sentinel / ".agents" / "keep.txt"
        sentinel_marker.write_text("untouched\n", encoding="utf-8")
        copy_package(package)

        polluted_env = {
            **os.environ,
            "GIT_DIR": str(ROOT / ".git"),
            "GIT_WORK_TREE": str(sentinel),
            "GIT_INDEX_FILE": str(root / "fake-index"),
        }
        result = run_setup(package, home, root, polluted_env)
        require(result.returncode == 0, result.stderr)

        installed = home / ".codex" / "skills"
        installed_names = {path.name for path in installed.iterdir()}
        require(USER_SKILLS <= installed_names, "not all user skills were installed")
        require(
            (installed / "jvc-research-core" / "scripts" / "researchctl.py").is_file(),
            "hidden research core was not installed",
        )
        require("  /jvc-research-core" not in result.stdout, "hidden core leaked into slash list")
        require("Support: 1 hidden component" in result.stdout, "hidden support count missing")
        require(
            f"✓ {COMPONENT_COUNT} components registered" in result.stdout,
            f"{COMPONENT_COUNT}-component success missing",
        )
        require(
            not (sentinel / ".agents" / "skills").exists(),
            "polluted Git environment redirected installation",
        )
        require(sentinel_marker.read_text(encoding="utf-8") == "untouched\n", "Git sentinel changed")

        backups = list(installed.glob("jvc-prescreen.backup.*"))
        require(len(backups) == 1, f"expected one recoverable backup, got {len(backups)}")
        backup_file = backups[0] / "original" / "user-customization.txt"
        require(backup_file.read_text(encoding="utf-8") == "keep me\n", "customization backup lost")
        require((installed / "jvc-prescreen" / "SKILL.md").is_file(), "replacement skill unusable")

        second = run_setup(package, home, root, polluted_env)
        require(second.returncode == 0, second.stderr)
        repeated_backups = list(installed.glob("jvc-prescreen.backup.*"))
        require(repeated_backups == backups, "repeat install created an unnecessary backup")
        require(backup_file.read_text(encoding="utf-8") == "keep me\n", "repeat install lost backup")

        missing_package = root / "missing-core-package"
        missing_home = root / "missing-home"
        (missing_home / ".codex").mkdir(parents=True)
        copy_package(missing_package)
        shutil.rmtree(missing_package / "skills" / "jvc-research-core")
        missing = run_setup(missing_package, missing_home, root, polluted_env)
        require(missing.returncode != 0, "missing core source should fail setup")
        require("missing source component" in missing.stderr, "missing source failure was unclear")
        require(
            f"✓ {COMPONENT_COUNT} components registered" not in missing.stdout,
            "missing source reported success",
        )
        require(
            not (missing_home / ".codex" / "skills").exists(),
            "setup wrote a target before source preflight completed",
        )

        windows_package = root / "windows-package"
        windows_home = root / "windows-home"
        fake_bin = root / "fake-bin"
        (windows_home / ".codex").mkdir(parents=True)
        fake_bin.mkdir()
        fake_uname = fake_bin / "uname"
        fake_uname.write_text("#!/usr/bin/env bash\necho MINGW64_NT\n", encoding="utf-8")
        fake_uname.chmod(0o755)
        copy_package(windows_package)
        windows_env = {
            **polluted_env,
            "PATH": f"{fake_bin}{os.pathsep}{polluted_env['PATH']}",
        }

        windows_first = run_setup(windows_package, windows_home, root, windows_env)
        require(windows_first.returncode == 0, windows_first.stderr)
        windows_skills = windows_home / ".codex" / "skills"
        require(not list(windows_skills.glob("*.backup.*")), "first Windows install made a backup")

        windows_second = run_setup(windows_package, windows_home, root, windows_env)
        require(windows_second.returncode == 0, windows_second.stderr)
        require(
            not list(windows_skills.glob("*.backup.*")),
            "identical Windows reinstall made duplicate backups",
        )

        customized_skill = windows_skills / "jvc-bull-case"
        (customized_skill / "user-customization.txt").write_text("preserve me\n", encoding="utf-8")
        windows_third = run_setup(windows_package, windows_home, root, windows_env)
        require(windows_third.returncode == 0, windows_third.stderr)
        windows_backups = list(windows_skills.glob("*.backup.*"))
        require(len(windows_backups) == 1, "Windows customization should back up one component")
        require(
            windows_backups[0].name.startswith("jvc-bull-case.backup."),
            "Windows backup belongs to the wrong component",
        )
        require(
            (windows_backups[0] / "original" / "user-customization.txt").read_text(
                encoding="utf-8"
            )
            == "preserve me\n",
            "Windows backup lost the customization",
        )
        require(
            tree_snapshot(customized_skill)
            == tree_snapshot(windows_package / "skills" / "jvc-bull-case"),
            "Windows replacement does not match its source",
        )

    print("research core install simulation passed")


if __name__ == "__main__":
    main()
