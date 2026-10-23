"""Fuzzes the parsers in scripts/check.py with Atheris.

Run with: python fuzz/fuzz_check.py -max_total_time=60 fuzz/corpus

fuzz/corpus holds real SKILL.md files as seeds: the checks only run on text
that starts with frontmatter, which random bytes almost never produce.
"""

import pathlib
import re
import sys

import atheris

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

with atheris.instrument_imports():
    import check


def test_one_input(data):
    fdp = atheris.FuzzedDataProvider(data)
    directory = fdp.ConsumeUnicodeNoSurrogates(32)
    text = fdp.ConsumeUnicodeNoSurrogates(8192)

    fields = check.frontmatter(text)
    assert fields is None or all(isinstance(k, str) and isinstance(v, str) for k, v in fields.items())

    problems = check.skill_problems(text, directory)
    assert all(isinstance(p, str) for p in problems)
    # A file without frontmatter is always reported.
    assert fields is not None or problems == ["no frontmatter at the top of the file"]

    for target in check.relative_links(text):
        assert target
        assert not any(c.isspace() or c in ")#" for c in target)
        assert not re.match(r"[a-z]+:", target)


def main():
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
