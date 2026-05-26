---
name: multi-agent-dispatcher
description: >
  Use when the user asks for multi-agent work, delegation, sub-agents, parallel
  agents, 并行处理, 委托, 多智能体, 多 Agent, sub-agent, agent 分工, DAG 调度,
  分头处理, 分别派, 拆给不同 agent, worktree-based parallel execution, or a
  long-running multi-agent engineering loop with resumable state and verification
  evidence. This skill helps the manager run large delegated tasks through a
  closed loop: spec, DAG, bounded sub-agent tasks, progress ledger, evidence-based
  verification, stop/rollback, merge, and handoff. Do not use for ordinary
  single-agent coding or analysis.
---

# Multi-Agent Dispatcher

Use this skill when the user asks for or clearly authorizes multiple agents, delegated work, parallel stages, or worktree isolation. Multi-agent work is treated as a long-task engineering loop by default.

Do not silently infer multi-agent execution merely because a task is broad. If multi-agent work seems useful but the user has not authorized it, propose it briefly or proceed as a single agent according to the normal task flow.

The manager owns scheduling, state, merge, and final acceptance. Sub-agents own bounded execution units.

## Core Loop

Run multi-agent tasks through this sequence:

```text
Context Intake -> Spec -> Artifact Directory -> DAG / Stage Gate -> Sub-Agent Execution -> Progress Ledger -> Verification -> Stop/Rollback Check -> Merge -> Handoff
```

Use real delegation or sub-agent tools only when they are available. When the user explicitly asks for real sub-agents, check the active tools or tool discovery if available before falling back. If no such tool is available, do not pretend to run parallel agents; create the DAG and execute stages sequentially or explain the limitation.

## When To Apply

Apply this skill when at least one is true:

- The user explicitly asks for multiple agents, sub-agents, delegation, parallel agents, DAG scheduling, or worktree isolation.
- The user asks to split agent work across independently owned tracks such as frontend, backend, tests, docs, data migration, or evaluator.
- The user asks for a multi-agent task that must be resumable, verified, or continued across sessions.
- The user says agents may be used if useful, and the task is genuinely parallelizable with clear ownership boundaries.

Do not use this for small edits, simple questions, direct command results, or ordinary single-agent coding where one agent can finish and verify locally.

High-impact operations such as production data, publishing, permissions, paid APIs, or destructive actions do not independently trigger this skill. They are escalation and stop conditions after a multi-agent workflow has already been authorized.

## Operating Modes

- **Lightweight mode:** For moderate delegated work, keep the spec and ledger brief. Continue executing unless a hard stop condition appears.
- **Alignment mode:** For ambiguous plans, architecture, agent ownership, or dependency trees, ask one question at a time until shared understanding is good enough to build the DAG. Each question must include the manager's recommended answer.
- **Full artifact mode:** For long, risky, resumable, or truly parallel work, write durable artifacts and update them at stage boundaries.

Do not block ordinary implementation just to ask for plan approval. Pause only when scope, risk, ambiguity, destructive operations, or repeated verification failures make a wrong decision expensive.

## Artifacts

Prefer existing project planning, issue, or workspace conventions. If none exist, place artifacts under `<active-project-root>/workspace/<task-slug>/`.

Recommended files:

- `task_spec.md`: goal, non-goals, constraints, acceptance criteria, verification evidence, risks, budget, and stop conditions.
- `progress.md`: current goal, completed work, changed files, decisions, commands, evidence, risks, and next step.
- `X.Y-<agent>.md`: each sub-agent report.
- `evaluator_report.md`: pass/fail evidence for high-risk, UI, release, or user-facing tasks.

Use templates in `templates/` when no project-specific format exists.

For full artifact mode, prefer the bundled initializer instead of hand-creating files:

```bash
python3 <skill-dir>/scripts/init_run.py --project-root <active-project-root> --title "<task title>" --agents frontend,backend,tests
```

## Context Intake

Before planning:

- Read the project `AGENTS.md`, docs, existing plans, previous ledgers, and relevant files.
- If the user asks to continue, locate the prior artifact directory and read the previous ledger/reports before editing.
- Check for previous sub-agent runs, reports, worktrees, or temporary resources that should be reused, closed, or left untouched.
- If the user explicitly asked for real sub-agents, confirm the available delegation mechanism before assigning work.
- Inspect git status before using worktrees. Do not overwrite or revert unrelated user changes.

## Question-Driven Alignment

Use this only before the DAG is stable, not as a general habit. It is most useful when the user asks to align on a plan, explore the design tree, resolve dependencies, or establish shared understanding before execution.

Process:

1. State the current understanding in one short paragraph.
2. Identify the next unresolved branch or dependency.
3. Ask exactly one question.
4. Give the recommended answer and why it is the default.
5. After the user answers, update the spec/DAG and move to the next unresolved branch.

Stop asking and start executing when the remaining uncertainty no longer affects agent ownership, irreversible decisions, verification strategy, or user-facing behavior. Do not use this mode for small edits or already-scoped implementation tasks.

## Spec And Stage Gate

Before spawning sub-agents, define:

- Goal, non-goals, constraints, acceptance criteria, and stop conditions.
- Artifact directory.
- Stage number and dependencies.
- File or responsibility ownership for each sub-agent.
- Verification expected from each sub-agent.
- Merge order and conflict handling.
- What the manager should do locally while agents run.

Model the work as a DAG: parallel tasks share the same stage number; dependent tasks move to later stages.

## Worktree Isolation

For code changes that can conflict or proceed independently, prefer physical isolation with `git worktree` when the repository state allows it. Do not use worktrees for tiny edits, non-code analysis, or tasks where file ownership cannot be separated.

```bash
git worktree add -b feature/<topic>-frontend ../wt-<topic>-frontend
git worktree add -b feature/<topic>-backend ../wt-<topic>-backend
git worktree add -b feature/<topic>-tests ../wt-<topic>-tests
```

Use the project's own branch policy, test commands, and workflow docs over generic templates.

## Sub-Agent Contract

Keep sub-agent tasks concrete, bounded, and independently verifiable. Give each sub-agent disjoint file ownership or responsibility ownership.

Ask each sub-agent to return only four lines:

```text
状态：已完成 / 失败 / 需要决策
报告：<artifact-dir>/X.Y-xxx.md
产出：N 个文件（列出路径）
决策点：[如有，一句话描述]
```

For larger findings, require a report file under `<artifact-dir>/` instead of pasting the report into chat.

Each report should include: goal, files touched, commands run, evidence, unresolved risks, assumptions that affect merging, and any stub/TODO/mock/unverified path.

When a sub-agent returns a report path, validate its structure before relying on it:

```bash
python3 <skill-dir>/scripts/validate_report.py <artifact-dir>/X.Y-xxx.md --type subagent
```

## Verification

Sub-agents may report evidence, but the manager or an evaluator owns final acceptance.

Prefer external evidence over self-assessment:

- Machine checks: tests, typecheck, lint, build, schema validation, data readback.
- Environment checks: browser interaction, screenshots, API round trips, database state, logs.
- Independent evaluation: evaluator agent, focused review, CI, or a strict rubric.

Reject outputs that package stubs, TODOs, mocks, or untested critical paths as completion. For Web/UI work, browser-level verification is required when a browser is available and the UI path matters.

## Stop And Rollback

Stop and re-plan instead of adding more agents when:

- Scope expands materially beyond the spec.
- The same stage fails verification twice without a new diagnosis.
- A sub-agent needs destructive, publishing, permission, paid, or production-data operations.
- File ownership conflicts between agents.
- The task depends on unavailable credentials, services, or environments.
- Multiple viable paths remain and the choice affects product or maintenance direction.

Preserve rollback paths such as git diff, worktree isolation, backups, dry-runs, previews, readback checks, or old config values.

## Merge And Handoff

Merge only after reading reports and checking conflicts. Keep the manager context small: receive status, paths, short decisions, and verification results.

End with:

- What changed.
- Which reports and artifacts matter.
- Verification evidence.
- Decisions made.
- Residual risks.
- Next step or handoff state.

## Reference Loading

- Read `references/closed-loop-pattern.md` when designing or revising the orchestration loop.
- Read `references/roles.md` when deciding whether to spawn explorers, workers, evaluators, or mergers.
- Read `references/stop-conditions.md` when a task has high impact, ambiguous scope, repeated failures, or external side effects.
- Read `references/eval_cases.md` when testing whether this skill triggers and behaves correctly.
- Use `scripts/init_run.py` to create durable artifacts and `scripts/validate_report.py` to check reports.
- Use `templates/task_spec.md`, `templates/progress_ledger.md`, `templates/subagent_task.md`, `templates/subagent_report.md`, and `templates/evaluator_report.md` when scripts are not suitable.

---

*Multi-Agent Dispatcher v4.0.0 | 2026-05-26*
