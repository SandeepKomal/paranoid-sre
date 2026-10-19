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

errors = []


def check_skill(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{skill_md}: no frontmatter at the top of the file")
        return
    fields = {}
    for line in match.group(1).splitlines():
        if line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()

    for key in fields:
        if key not in ALLOWED_KEYS:
            errors.append(f"{skill_md}: frontmatter key {key!r} is rejected by Claude.ai and the API")
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append(f"{skill_md}: name {name!r} must be 1-64 lowercase letters, digits or hyphens")
    if "anthropic" in name or "claude" in name:
        errors.append(f"{skill_md}: name must not contain 'anthropic' or 'claude'")
    if name != skill_md.parent.name:
        errors.append(f"{skill_md}: name {name!r} does not match its directory {skill_md.parent.name!r}")
    description = fields.get("description", "")
    if not description:
        errors.append(f"{skill_md}: description is missing")
    if len(description) > 1024:
        errors.append(f"{skill_md}: description is {len(description)} characters, the limit is 1024")
    if "<" in description or ">" in description:
        errors.append(f"{skill_md}: description must not contain angle brackets")
    lines = len(text.splitlines())
    if lines > MAX_LINES:
        errors.append(f"{skill_md}: {lines} lines; keep SKILL.md under {MAX_LINES} and move detail to references")


def check_links(md):
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:", target):
            continue
        if not (md.parent / target).exists():
            errors.append(f"{md}: broken link to {target}")


skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
if not skills:
    errors.append("no skills/*/SKILL.md found")
for skill_md in skills:
    check_skill(skill_md)
for md in sorted(ROOT.rglob("*.md")):
    if ".git" not in md.parts:
        check_links(md)

for error in errors:
    print(error, file=sys.stderr)
if errors:
    sys.exit(1)
print(f"ok: {len(skills)} skill(s) checked")
