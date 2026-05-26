#!/usr/bin/env python3
"""Initialize a multi-agent run artifact directory."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


TEMPLATE_MAP = {
    "task_spec.md": "task_spec.md",
    "progress_ledger.md": "progress.md",
    "evaluator_report.md": "evaluator_report.md",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value or "multi-agent-task"


def copy_template(template_dir: Path, template_name: str, output_path: Path, force: bool) -> bool:
    if output_path.exists() and not force:
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_dir / template_name, output_path)
    return True


def write_task_from_template(template_dir: Path, output_path: Path, agent: str, index: int, force: bool) -> bool:
    if output_path.exists() and not force:
        return False
    content = (template_dir / "subagent_task.md").read_text(encoding="utf-8")
    content = content.replace("任务 X.Y: <任务名>", f"任务 1.{index}: {agent}")
    content = content.replace("<artifact-dir>", str(output_path.parent.parent))
    content = content.replace("X.Y-报告.md", f"1.{index}-{agent}-report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a multi-agent artifact directory from templates.")
    parser.add_argument("--project-root", default=".", help="Project root where workspace/<slug> will be created.")
    parser.add_argument("--slug", help="Stable task slug. Derived from --title when omitted.")
    parser.add_argument("--title", default="multi-agent-task", help="Human-readable task title.")
    parser.add_argument("--agents", default="", help="Comma-separated agent task names, e.g. frontend,backend,tests.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    slug = slugify(args.slug or args.title)
    artifact_dir = project_root / "workspace" / slug
    template_dir = Path(__file__).resolve().parents[1] / "templates"

    created = []
    skipped = []

    for template_name, output_name in TEMPLATE_MAP.items():
        output_path = artifact_dir / output_name
        if copy_template(template_dir, template_name, output_path, args.force):
            created.append(output_path)
        else:
            skipped.append(output_path)

    agents = [slugify(item) for item in args.agents.split(",") if item.strip()]
    for index, agent in enumerate(agents, start=1):
        output_path = artifact_dir / "tasks" / f"1.{index}-{agent}.md"
        if write_task_from_template(template_dir, output_path, agent, index, args.force):
            created.append(output_path)
        else:
            skipped.append(output_path)

    print(f"artifact_dir={artifact_dir}")
    if created:
        print("created:")
        for path in created:
            print(f"- {path}")
    if skipped:
        print("skipped_existing:")
        for path in skipped:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
