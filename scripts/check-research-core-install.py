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
    "jvc-meeting-notes",
    "jvc-interview-prep",
    "jvc-prescreen",
    "jvc-business-economics",
    "jvc-track-research",
    "jvc-workbook",
    "jvc-thesis-test",
    "jvc-ic-memo",
    "jvc-dd-report-digest",
    "jvc-portfolio-tracking",
}
SUPPORT_COMPONENTS = {"jvc-research-core", "jvc-research-report", "jvc-knowledge-tree-builder"}
RETIRED_SKILLS = {"jvc-bear-case", "jvc-claim-audit", "jvc-deal-flow", "jvc-market-sizing"}
COMPONENT_COUNT = len(USER_SKILLS | SUPPORT_COMPONENTS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def copy_package(destination: Path) -> None:
    destination.mkdir()
    shutil.copy2(ROOT / "setup", destination / "setup")
    shutil.copytree(ROOT / "skills", destination / "skills",
                    ignore=shutil.ignore_patterns("roi-modeler-template.xlsx"))


def clean_env(home: Path, ceiling: Path, base: Mapping[str, str]) -> dict[str, str]:
    env = {key: value for key, value in base.items() if not key.startswith("GIT_")}
    env.update({"HOME": str(home), "GIT_CEILING_DIRECTORIES": str(ceiling)})
    return env


def run_setup(
    package: Path,
    home: Path,
    ceiling: Path,
    base_env: Mapping[str, str],
    args: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    env = clean_env(home, ceiling, base_env)
    git_keys = {key for key in env if key.startswith("GIT_")}
    require(
        git_keys == {"GIT_CEILING_DIRECTORIES"},
        f"Git variables leaked into install environment: {sorted(git_keys)}",
    )
    return subprocess.run(
        ["bash", str(package / "setup"), *args],
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
        require(USER_SKILLS <= installed_names, "not all primary skills were installed")
        require(not (RETIRED_SKILLS & installed_names), "retired skills were installed")
        require("Skills: 10 primary skills" in result.stdout, "primary count missing")
        require(not (installed / "jvc-invoice-manager").exists(), "operations installed by default")
        for name in SUPPORT_COMPONENTS:
            require((installed / name / "SKILL.md").is_file(), "missing support: " + name)
            require("user_invocable: false" in (installed / name / "SKILL.md").read_text(),
                    "support still user-invocable: " + name)
            require(f"  /{name}" not in result.stdout, "support leaked into slash list")
        for name in USER_SKILLS:
            require(f"  /{name}" in result.stdout, "primary entry missing from slash list: " + name)
        require(
            (installed / "jvc-research-core" / "scripts" / "researchctl.py").is_file(),
            "hidden research core was not installed",
        )
        require("  /jvc-research-core" not in result.stdout, "hidden core leaked into slash list")
        require("Support: 3 hidden components" in result.stdout, "hidden support count missing")
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

        # Default reinstallation preserves a previously installed optional tool.
        old_operations = installed / "jvc-invoice-manager"
        old_operations.mkdir()
        (old_operations / "user-data.txt").write_text("keep existing operations")
        second = run_setup(package, home, root, polluted_env)
        require((old_operations / "user-data.txt").read_text() == "keep existing operations",
                "default setup modified the old operations installation")
        require(second.returncode == 0, second.stderr)
        repeated_backups = list(installed.glob("jvc-prescreen.backup.*"))
        require(repeated_backups == backups, "repeat install created an unnecessary backup")
        require(backup_file.read_text(encoding="utf-8") == "keep me\n", "repeat install lost backup")

        # Global registration uses one shared source and skips physical aliases.
        global_package = root / "global-package"
        global_home = root / "global-home"
        (global_home / ".claude" / "skills" / "jvc-prescreen").mkdir(parents=True)
        (global_home / ".claude" / "skills" / "jvc-prescreen" / "user-customization.txt").write_text(
            "restore me\n", encoding="utf-8"
        )
        for client_dir in (
            ".codex",
            ".hermes/skills",
            ".cursor/skills",
            ".config/opencode/skills",
            ".pi/agent/skills",
            ".grok/skills",
        ):
            (global_home / client_dir).mkdir(parents=True)
        (global_home / ".openclaw").mkdir()
        (global_home / ".openclaw" / "skills").symlink_to(
            global_home / ".claude" / "skills", target_is_directory=True
        )
        copy_package(global_package)
        global_result = run_setup(global_package, global_home, root, polluted_env, ("--global",))
        require(global_result.returncode == 0, global_result.stderr)
        require("Skills: 10 primary skills" in global_result.stdout, "global primary count missing")
        require("Support: 3 hidden components" in global_result.stdout, "global support count missing")
        global_targets = [
            global_home / ".agents/skills",
            global_home / ".claude/skills",
            global_home / ".codex/skills",
            global_home / ".hermes/skills",
            global_home / ".cursor/skills",
            global_home / ".openclaw/skills",
            global_home / ".config/opencode/skills",
            global_home / ".pi/agent/skills",
            global_home / ".grok/skills",
        ]
        for target in global_targets:
            require(target.is_dir(), f"global target missing: {target}")
            for name in USER_SKILLS | SUPPORT_COMPONENTS:
                entry = target / name
                source = global_package / "skills" / name
                require(entry.is_dir() and (entry / "SKILL.md").is_file(),
                        f"global component unreadable: {entry}")
                require(entry.is_symlink(), f"global component is not source-linked: {entry}")
                require(os.path.realpath(entry) == os.path.realpath(source),
                        f"global component has a different source: {entry}")
        require(global_result.stdout.count(f"✓ {COMPONENT_COUNT} components registered") == 8,
                "global aliases were not physically deduplicated")
        require(not (global_package / ".agents").exists(), "global install wrote the project")
        require(not (global_home / ".unused/skills").exists(), "global install created an uninstalled client")
        global_backups = sorted(
            (global_home / ".local/state/jvc-analyst/backups").rglob("*.backup.*")
        )
        require(len(global_backups) == 1, "global install did not keep one custom backup")
        require(global_backups[0].parent.parent == global_home / ".local/state/jvc-analyst/backups",
                "global backup is inside a discovery directory")
        restored = root / "restored-global-customization"
        shutil.copytree(global_backups[0] / "original", restored)
        require((restored / "user-customization.txt").read_text(encoding="utf-8") == "restore me\n",
                "global custom backup is not restorable")
        global_before = [path.relative_to(global_home).as_posix() for path in global_backups]
        global_again = run_setup(global_package, global_home, root, polluted_env, ("--global",))
        require(global_again.returncode == 0, global_again.stderr)
        global_after = [
            path.relative_to(global_home).as_posix()
            for path in (global_home / ".local/state/jvc-analyst/backups").rglob("*.backup.*")
        ]
        require(global_after == global_before, "global reinstall is not idempotent")

        # Global operations are a separate one-component install (outside the default research set).
        global_operations_home = root / "global-operations-home"
        (global_operations_home / ".codex").mkdir(parents=True)
        global_operations = run_setup(
            global_package, global_operations_home, root, polluted_env, ("--global", "--operations")
        )
        require(global_operations.returncode == 0, global_operations.stderr)
        operations_global_targets = [
            global_operations_home / ".agents/skills",
            global_operations_home / ".codex/skills",
        ]
        for target in operations_global_targets:
            require({path.name for path in target.iterdir()} == {"jvc-invoice-manager"},
                    "global operations installed research components")
            require((target / "jvc-invoice-manager").is_symlink(),
                    "global operations source link missing")
        require("Skills: 0 primary skills" in global_operations.stdout,
                "global operations retained research menu")
        require("1 components registered" in global_operations.stdout,
                "global operations count wrong")
        require(not (global_operations_home / ".config/opencode/skills").exists(),
                "global operations created an uninstalled client")

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

        # An operations-only source pack needs neither the core nor research skills.
        operations_package = root / "operations-only"
        operations_package.mkdir()
        shutil.copy2(ROOT / "setup", operations_package / "setup")
        shutil.copytree(ROOT / "skills/jvc-invoice-manager",
                        operations_package / "skills/jvc-invoice-manager")
        operations_home = root / "operations-home"
        (operations_home / ".codex").mkdir(parents=True)
        operations = run_setup(operations_package, operations_home, root, polluted_env, ("--operations",))
        require(operations.returncode == 0, operations.stderr)
        operations_names = {p.name for p in (operations_home / ".codex/skills").iterdir()}
        require(operations_names == {"jvc-invoice-manager"}, "operations installed research components")
        require("  /jvc-invoice-manager" in operations.stdout, "operations command missing")
        require("1 components registered" in operations.stdout, "operations count wrong")
        again = run_setup(operations_package, operations_home, root, polluted_env, ("--operations",))
        require(again.returncode == 0 and not list((operations_home / ".codex/skills").glob("*.backup.*")),
                "operations reinstall is not idempotent")
        invalid_home = root / "invalid-home"
        (invalid_home / ".codex").mkdir(parents=True)
        for args in (("--bad-option",), ("--operations", "extra"), ("--global", "--bad-option")):
            invalid = run_setup(package, invalid_home, root, polluted_env, args)
            require(invalid.returncode == 2, "invalid options accepted")
            require(not (invalid_home / ".codex/skills").exists(), "invalid options caused writes")

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

        customized_skill = windows_skills / "jvc-thesis-test"
        (customized_skill / "user-customization.txt").write_text("preserve me\n", encoding="utf-8")
        windows_third = run_setup(windows_package, windows_home, root, windows_env)
        require(windows_third.returncode == 0, windows_third.stderr)
        windows_backups = list(windows_skills.glob("*.backup.*"))
        require(len(windows_backups) == 1, "Windows customization should back up one component")
        require(
            windows_backups[0].name.startswith("jvc-thesis-test.backup."),
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
            == tree_snapshot(windows_package / "skills" / "jvc-thesis-test"),
            "Windows replacement does not match its source",
        )

    print("research core install simulation passed")


if __name__ == "__main__":
    main()
