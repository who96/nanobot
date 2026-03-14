"""Tests for skill enable/disable toggle functionality."""

from pathlib import Path

from nanobot.agent.skills import SkillsLoader


def _create_skill(skills_dir: Path, name: str, frontmatter: str = "") -> Path:
    """Create a minimal SKILL.md file in a skill directory."""
    skill_dir = skills_dir / name
    skill_dir.mkdir(parents=True)
    content = f"---\nname: {name}\ndescription: Test skill {name}\n{frontmatter}---\n\n# {name}\nSkill content."
    (skill_dir / "SKILL.md").write_text(content)
    return skill_dir


def test_disabled_skill_excluded_from_list(tmp_path: Path) -> None:
    """A skill with enabled: false should not appear in list_skills()."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skills_dir = workspace / "skills"

    _create_skill(skills_dir, "active-skill")
    _create_skill(skills_dir, "disabled-skill", "enabled: false\n")

    loader = SkillsLoader(workspace, builtin_skills_dir=tmp_path / "no-builtins")
    names = [s["name"] for s in loader.list_skills()]

    assert "active-skill" in names
    assert "disabled-skill" not in names


def test_enabled_skill_included(tmp_path: Path) -> None:
    """A skill with enabled: true should appear normally."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skills_dir = workspace / "skills"

    _create_skill(skills_dir, "explicit-enabled", "enabled: true\n")

    loader = SkillsLoader(workspace, builtin_skills_dir=tmp_path / "no-builtins")
    names = [s["name"] for s in loader.list_skills()]

    assert "explicit-enabled" in names


def test_no_enabled_field_defaults_to_true(tmp_path: Path) -> None:
    """Omitting the enabled field should default to enabled (backward compat)."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skills_dir = workspace / "skills"

    _create_skill(skills_dir, "legacy-skill")

    loader = SkillsLoader(workspace, builtin_skills_dir=tmp_path / "no-builtins")
    names = [s["name"] for s in loader.list_skills()]

    assert "legacy-skill" in names


def test_disabled_skill_shown_in_summary_as_unavailable(tmp_path: Path) -> None:
    """Disabled skills should appear in summary with available=false and <disabled/>."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skills_dir = workspace / "skills"

    _create_skill(skills_dir, "off-skill", "enabled: false\n")

    loader = SkillsLoader(workspace, builtin_skills_dir=tmp_path / "no-builtins")
    summary = loader.build_skills_summary()

    assert 'available="false"' in summary
    assert "<disabled/>" in summary
    assert "off-skill" in summary


def test_disabled_skill_still_loadable(tmp_path: Path) -> None:
    """Even disabled skills can be loaded directly by name (for inspection)."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    skills_dir = workspace / "skills"

    _create_skill(skills_dir, "paused-skill", "enabled: false\n")

    loader = SkillsLoader(workspace, builtin_skills_dir=tmp_path / "no-builtins")
    content = loader.load_skill("paused-skill")

    assert content is not None
    assert "paused-skill" in content
