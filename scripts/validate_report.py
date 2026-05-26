#!/usr/bin/env python3
"""Validate required Markdown sections for multi-agent artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_SECTIONS = {
    "subagent": [
        "Goal",
        "Files Touched",
        "Commands Run",
        "Evidence",
        "Unresolved Risks",
        "Assumptions Affecting Merge",
        "Stub TODO Mock Or Unverified Path",
        "Return Summary",
    ],
    "evaluator": [
        "Scope Checked",
        "Evidence",
        "Blocking Issues",
        "Non-Blocking Issues",
        "Stub Or Placeholder Check",
        "Required Fixes",
        "Residual Risk",
    ],
    "progress": [
        "Artifact Location",
        "Current Goal",
        "Completed",
        "Changed Files",
        "Decisions",
        "Commands And Evidence",
        "Verification",
        "Open Risks",
        "Stop Conditions Checked",
        "Next Step",
    ],
    "spec": [
        "Goal",
        "User-Facing Outcome",
        "Non-Goals",
        "Constraints",
        "Acceptance Criteria",
        "Verification Evidence",
        "Risks",
        "Budget",
        "Stop Conditions",
        "Artifact Location",
    ],
}


def extract_headings(markdown: str) -> set[str]:
    headings = set()
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            headings.add(match.group(1).strip())
    return headings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a multi-agent Markdown artifact.")
    parser.add_argument("path", help="Markdown file to validate.")
    parser.add_argument(
        "--type",
        choices=sorted(REQUIRED_SECTIONS),
        required=True,
        help="Artifact type to validate.",
    )
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"FAIL missing file: {path}")
        return 2

    headings = extract_headings(path.read_text(encoding="utf-8"))
    required = set(REQUIRED_SECTIONS[args.type])
    missing = sorted(required - headings)

    if missing:
        print(f"FAIL {path}")
        print("missing_sections:")
        for section in missing:
            print(f"- {section}")
        return 1

    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
