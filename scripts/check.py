#!/usr/bin/env python3
"""Checks the skill against the rules Claude.ai and the Skills API enforce on
upload, which are stricter than Claude Code's, and that every relative link
in the skill points at a file that exists."""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_LINES = 500


def frontmatter(text):
    """Returns the frontmatter fields of a SKILL.md, or None if it has none."""
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def skill_problems(text, directory):
    """Returns what Claude.ai or the Skills API would reject in a SKILL.md
    whose folder is called directory."""
    fields = frontmatter(text)
    if fields is None:
        return ["no frontmatter at the top of the file"]
    problems = []
    for key in fields:
        if key not in ALLOWED_KEYS:
            problems.append(f"frontmatter key {key!r} is rejected by Claude.ai and the API")
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        problems.append(f"name {name!r} must be 1-64 lowercase letters, digits or hyphens")
    if "anthropic" in name or "claude" in name:
        problems.append("name must not contain 'anthropic' or 'claude'")
    if name != directory:
        problems.append(f"name {name!r} does not match its directory {directory!r}")
    description = fields.get("description", "")
    if not description:
        problems.append("description is missing")
    if len(description) > 1024:
        problems.append(f"description is {len(description)} characters, the limit is 1024")
    if "<" in description or ">" in description:
        problems.append("description must not contain angle brackets")
    lines = len(text.splitlines())
    if lines > MAX_LINES:
        problems.append(f"{lines} lines; keep SKILL.md under {MAX_LINES} and move detail to references")
    return problems


def relative_links(text):
    """Returns the relative link targets in Markdown text."""
    return [
        target
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text)
        if not re.match(r"[a-z]+:", target)
    ]


def main():
    errors = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("no skills/*/SKILL.md found")
    for skill_md in skills:
        text = skill_md.read_text(encoding="utf-8")
        errors += [f"{skill_md}: {p}" for p in skill_problems(text, skill_md.parent.name)]
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        for target in relative_links(md.read_text(encoding="utf-8")):
            if not (md.parent / target).exists():
                errors.append(f"{md}: broken link to {target}")

    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"ok: {len(skills)} skill(s) checked")


if __name__ == "__main__":
    main()
