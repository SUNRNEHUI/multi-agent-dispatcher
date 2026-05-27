# Multi-Agent Dispatcher

**A harness protocol for large, resumable, evidence-verified multi-agent work.**

> v5 evolves the project from protocol guidance into a manager-enforced dispatch harness: the main agent must gate capabilities, advance a state machine, require acceptance evidence, enforce budget stops, keep traceable state, and adapt the same core protocol to different agent runtimes.

---

## What It Solves

Multi-agent work usually fails in predictable ways:

- The manager loses state after context grows.
- Sub-agents overlap ownership and create merge conflicts.
- Reports become long chat transcripts instead of reusable artifacts.
- Executors mark unfinished stubs or unverified UI as complete.
- High-impact operations continue without a clear stop or rollback point.

This skill treats the filesystem as durable task state and makes the manager responsible for convergence. In v5, the important change is not more process; it is that the process becomes a protocol the manager must run before it can claim completion.

It also avoids over-delegation: if the user asks for multi-agent execution on a tiny task, the manager first decides whether dispatch is actually useful. Small edits should be completed directly by one agent.

---

## User Benefits

### Resumable Long Tasks

Task state is written under `<project>/workspace/<task-slug>/`, so the manager can resume from previous specs, ledgers, reports, and handoffs.

### Cleaner Delegation

Each sub-agent gets bounded ownership: files, responsibility, expected report, evidence, and stop conditions.

### Evidence-Based Completion

Sub-agent completion is not final completion. The manager or evaluator verifies with tests, build output, browser checks, readback, logs, screenshots, or CI evidence.

### Harness-Level Control

The manager does not merely suggest good behavior. It runs protocol gates:

- **Capability gate:** confirm which runtime controls are actually available before assigning work.
- **State machine:** move the task through named states instead of drifting through chat.
- **Acceptance registry:** bind each acceptance criterion to evidence and an owner.
- **Budget circuit breaker:** stop when context, time, cost, retries, or tool calls exceed the stage budget.
- **Trace:** record key decisions, commands, evidence, and stop reasons in durable files.
- **Runtime adapters:** map the same core protocol onto Codex, Claude Code, or another harness without changing the task semantics.

### Safer High-Impact Work

Production data, publishing, permission changes, paid APIs, destructive actions, repeated failures, and ownership conflicts trigger stop/re-plan behavior.

### Better Alignment Before Dispatch

When the plan is unclear, alignment mode asks exactly one question at a time and includes the manager's recommended answer.

---

## When To Use

Load this skill when the user explicitly asks for:

- multi-agent work
- sub-agents
- delegation
- parallel agents
- DAG scheduling
- worktree-based parallel execution
- 分头处理 / 分别派 / 拆给不同 agent
- multi-agent work that must be resumable or evidence-verified

Loading the skill does not mean dispatching agents. The manager first runs a right-sizing gate. If the task is small, localized, or cheaper to complete directly, it should skip multi-agent orchestration and finish as a single agent.

Do **not** use it merely because a task is large. If the user has not authorized multi-agent execution, propose it briefly or proceed as a single agent.

---

## Operating Loop

```text
Context Intake
-> Right-Sizing Gate
-> Capability Gate
-> Spec / Acceptance Registry
-> Artifact Directory
-> State Machine Stage Gate
-> Bounded Execution
-> Trace / Progress Ledger
-> Verification / Evaluator
-> Budget / Stop Check
-> Merge
-> Handoff
```

The manager owns scheduling, state, merge, and final acceptance. Sub-agents own bounded execution units.

## v5 Harness Protocol

The harness protocol is the stable core that remains the same across runtimes.

### 1. Right-Sizing Gate

Explicit multi-agent wording authorizes the manager to evaluate dispatch; it does not force dispatch.

Dispatch is justified when the task has independent ownership surfaces, long or resumable scope, material verification risk, evaluator value, or isolation/rollback value.

Dispatch is not justified for typo fixes, small copy edits, direct commands, one-file changes, simple config tweaks, or narrow local bugs. In those cases the manager should say briefly that multi-agent overhead is unnecessary, execute directly, and verify normally.

### 2. Capability Gate

Before delegating, the manager records what is available in the current runtime:

- real sub-agent or delegation mechanism
- filesystem write access
- shell and sandbox limits
- worktree support
- browser or UI verification capability
- hook or instruction files that can carry protocol rules
- external services, credentials, and network assumptions

If a capability is missing, the manager must choose a fallback: execute sequentially, narrow scope, ask for a decision, or stop. It must not pretend that unavailable parallelism, browser checks, or evaluator isolation happened.

### 3. State Machine

The task advances through explicit states:

```text
INTAKE -> GATED -> SPECIFIED -> DISPATCHED -> REPORTED -> EVALUATING -> ACCEPTED -> HANDED_OFF
```

Stop states are first-class:

```text
BLOCKED -> NEEDS_DECISION -> FAILED
```

Each transition should leave a compact trace entry: current state, reason, owner, evidence path, and next state.

### 4. Acceptance Registry

Acceptance criteria are tracked as records, not prose. Each record should contain:

- criterion
- owner
- required evidence
- current status: `pending`, `pass`, `fail`, `blocked`, or `scoped_out`
- evidence path or command result summary

The manager cannot claim completion while any required registry item is not `pass` or explicitly `scoped_out` by user decision.

### 5. Budget Circuit Breaker

Each stage should have a small budget envelope: time, context, tool calls, retries, cost, and external side effects. When the stage breaches the envelope, the manager stops and records whether to continue, split, reduce scope, or ask the user.

The circuit breaker is meant to preserve resumability and prevent hidden burn, not to optimize for arbitrary limits.

### 6. Trace

Trace is the minimum durable evidence needed to resume and audit:

- capability gate result
- state transitions
- worker report paths
- evaluator result
- budget stop or retry reason
- final acceptance registry

Trace can live in the progress ledger or a dedicated file when the run is complex. Chat alone is not durable state.

### 7. Runtime Adapters

Adapters explain how the same protocol maps onto each runtime's controls. They do not change the protocol.

- Codex adapter: [`adapters/codex.md`](adapters/codex.md)
- Claude Code adapter: [`adapters/claude-code.md`](adapters/claude-code.md)
- Harness reference: [`references/harness-protocol.md`](references/harness-protocol.md)

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
├── adapters/
│   ├── claude-code.md
│   └── codex.md
├── master-prompt.md
├── sub-prompt.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── closed-loop-pattern.md
│   ├── eval_cases.md
│   ├── harness-protocol.md
│   ├── roles.md
│   └── stop-conditions.md
├── scripts/
│   ├── init_run.py
│   └── validate_report.py
└── templates/
    ├── acceptance_registry.json
    ├── capability_snapshot.md
    ├── evaluator_report.md
    ├── progress_ledger.md
    ├── run_state.json
    ├── subagent_report.md
    ├── subagent_task.md
    ├── task_spec.md
    └── trace.jsonl
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
├── acceptance_registry.json
├── capability_snapshot.md
├── task_spec.md
├── progress.md
├── run_state.json
├── trace.jsonl
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

When `acceptance_registry.json` or `run_state.json` sits next to `task_spec.md`, `progress.md`, or `evaluator_report.md`, validation also checks those protocol files.

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

## Runtime Adapters

The v5 protocol is runtime-neutral. Adapters document the practical control points:

- where persistent instructions live
- how tools and sandbox limits are discovered
- how worktrees and file ownership are enforced
- whether browser verification is available
- how sub-agents or sequential fallbacks are represented
- how hooks or local instruction files preserve the protocol
- where trace and acceptance records should be written

Start with the adapter for the runtime you are actually using, then run the same capability gate and acceptance registry either way.

---

## v5.0.1 Highlights

- Added a right-sizing gate before capability checks and DAG creation.
- Clarified that explicit multi-agent wording authorizes evaluation, not automatic dispatch.
- Added guidance to skip worker creation, worktrees, and artifacts for small tasks.
- Updated runtime adapters and eval cases to prevent coordination overhead on one-agent work.

## v5.0.0 Highlights

- Upgraded the skill from protocol guidance into a manager-enforced harness protocol.
- Added capability gate expectations and durable capability snapshots.
- Added `run_state.json` for explicit run, stage, and task state.
- Added `acceptance_registry.json` so completion is tied to evidence.
- Added `trace.jsonl` for resumable and auditable run events.
- Added evaluator result validation with `PASS`, `FAIL`, or `BLOCKED`.
- Added runtime adapters for Codex and Claude Code-style harnesses.
- Added v5 eval cases for capability fallback, evaluator failure, registry blocking, and budget stops.

## Upgrade Notes

v5 keeps the public skill purpose the same, but tightens the manager's responsibilities:

- Treat multi-agent work as a protocol run, not a chat-only checklist.
- Record actual runtime capabilities before dispatching workers.
- Keep acceptance criteria in `acceptance_registry.json` and require evidence before completion.
- Keep run progress in `run_state.json`, `progress.md`, and `trace.jsonl` so another manager can resume.
- Use runtime adapters only to map the same protocol onto Codex, Claude Code, or similar harnesses.

Existing v4 prompts and templates still map cleanly to v5, but long or risky tasks should use the new full artifact set.

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

**v5.0.1** · 2026-05-27

Previous public version: **v5.0.0** · 2026-05-26
