# Multi-Agent Dispatcher

**A file-driven multi-agent orchestration skill for large, resumable, evidence-verified agent work.**

> v4.0.0 changes the project from a simple auto-dispatch prompt into a closed-loop multi-agent operating protocol: spec, DAG, bounded sub-agents, progress ledger, evidence verification, stop/rollback, merge, and handoff.

---

## What It Solves

Multi-agent work usually fails in predictable ways:

- The manager loses state after context grows.
- Sub-agents overlap ownership and create merge conflicts.
- Reports become long chat transcripts instead of reusable artifacts.
- Executors mark unfinished stubs or unverified UI as complete.
- High-impact operations continue without a clear stop or rollback point.

This skill treats the filesystem as durable task state and makes the manager responsible for convergence.

---

## User Benefits

### Resumable Long Tasks

Task state is written under `<project>/workspace/<task-slug>/`, so the manager can resume from previous specs, ledgers, reports, and handoffs.

### Cleaner Delegation

Each sub-agent gets bounded ownership: files, responsibility, expected report, evidence, and stop conditions.

### Evidence-Based Completion

Sub-agent completion is not final completion. The manager or evaluator verifies with tests, build output, browser checks, readback, logs, screenshots, or CI evidence.

### Safer High-Impact Work

Production data, publishing, permission changes, paid APIs, destructive actions, repeated failures, and ownership conflicts trigger stop/re-plan behavior.

### Better Alignment Before Dispatch

When the plan is unclear, alignment mode asks exactly one question at a time and includes the manager's recommended answer.

---

## When To Use

Use this skill when the user explicitly asks for:

- multi-agent work
- sub-agents
- delegation
- parallel agents
- DAG scheduling
- worktree-based parallel execution
- 分头处理 / 分别派 / 拆给不同 agent
- multi-agent work that must be resumable or evidence-verified

Do **not** use it merely because a task is large. If the user has not authorized multi-agent execution, propose it briefly or proceed as a single agent.

---

## Operating Loop

```text
Context Intake
-> Spec
-> Artifact Directory
-> DAG / Stage Gate
-> Sub-Agent Execution
-> Progress Ledger
-> Verification
-> Stop/Rollback Check
-> Merge
-> Handoff
```

The manager owns scheduling, state, merge, and final acceptance. Sub-agents own bounded execution units.

---

## Install

```bash
cp -R multi-agent-dispatcher ~/.codex/skills/
```

Then ask Codex for explicitly delegated work, for example:

```text
这个项目有前端、后端、测试三块，帮我用多个 agent 并行做，但要有验收证据。
```

---

## Repository Structure

```text
multi-agent-dispatcher/
├── SKILL.md
├── README.md
├── master-prompt.md
├── sub-prompt.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── closed-loop-pattern.md
│   ├── eval_cases.md
│   ├── roles.md
│   └── stop-conditions.md
├── scripts/
│   ├── init_run.py
│   └── validate_report.py
└── templates/
    ├── evaluator_report.md
    ├── progress_ledger.md
    ├── subagent_report.md
    ├── subagent_task.md
    └── task_spec.md
```

---

## Artifact Directory

For full artifact mode, initialize a run:

```bash
python3 scripts/init_run.py \
  --project-root /path/to/project \
  --title "Checkout Refactor" \
  --agents frontend,backend,tests
```

This creates:

```text
/path/to/project/workspace/checkout-refactor/
├── task_spec.md
├── progress.md
├── evaluator_report.md
└── tasks/
    ├── 1.1-frontend.md
    ├── 1.2-backend.md
    └── 1.3-tests.md
```

---

## Sub-Agent Return Contract

Each sub-agent returns only four lines:

```text
状态：已完成 / 失败 / 需要决策
报告：<artifact-dir>/X.Y-xxx.md
产出：N 个文件（列出路径）
决策点：[如有，一句话描述]
```

Detailed findings go into the report file, not chat.

---

## Report Validation

Validate a sub-agent report before relying on it:

```bash
python3 scripts/validate_report.py <artifact-dir>/1.1-frontend-report.md --type subagent
```

Supported artifact types:

- `spec`
- `progress`
- `subagent`
- `evaluator`

---

## Roles

The skill defines explicit role boundaries:

- **Manager:** owns spec, DAG, state, merge, and final acceptance.
- **Explorer:** answers scoped codebase questions; does not edit.
- **Worker:** implements a bounded slice with clear ownership.
- **Evaluator:** checks acceptance criteria and may return FAIL.
- **Merger:** reads reports, resolves conflicts, and runs integration verification.

See [`references/roles.md`](references/roles.md).

---

## v4.0.0 Highlights

- Reworked the skill around a closed-loop multi-agent protocol.
- Added alignment mode: one question at a time, with a recommended answer.
- Added artifact initialization via `scripts/init_run.py`.
- Added report structure validation via `scripts/validate_report.py`.
- Added durable templates for specs, progress ledgers, sub-agent reports, and evaluator reports.
- Added role boundaries for manager, explorer, worker, evaluator, and merger.
- Added explicit stop/rollback rules for high-impact operations and repeated failures.
- Added eval cases for trigger behavior, false positives, continuation, UI verification, and alignment mode.

---

## Version

**v4.0.0** · 2026-05-26

Previous public version: **v3.0** · 2026-04-23
