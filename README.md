# Multi-Agent Dispatcher

[简体中文](README.zh-CN.md) | English

**A mode router for direct work, lightweight coordination, and full multi-agent harness runs.**

> v5.1 makes the skill smaller in daily use: the manager first chooses Direct, Lite, or Full mode. Full Harness remains available for long, risky, resumable work, but small and medium tasks should avoid unnecessary artifacts, worker setup, and ceremony.

> v5.2 adds Superpowers-aware methods without replacing the router: TDD, parallel-agent discipline, fresh worker context, two-stage review, worktree isolation, and verification-before-completion can strengthen Lite and Full mode when the task justifies them.

> v5.2.1 makes public sharing cleaner: it adds explicit Superpowers acknowledgement, tightens skill trigger metadata, and adds a packaging helper for runtime-only installs.

---

## What It Solves

Multi-agent work usually fails in predictable ways:

- The manager loses state after context grows.
- Sub-agents overlap ownership and create merge conflicts.
- Reports become long chat transcripts instead of reusable artifacts.
- Executors mark unfinished stubs or unverified UI as complete.
- High-impact operations continue without a clear stop or rollback point.

This skill now starts with mode selection, not automatic harness setup:

- **Direct:** one agent handles the task directly, verifies normally, and skips dispatcher artifacts.
- **Lite:** the manager coordinates a small amount of decomposition or review without creating the full harness directory.
- **Full:** the manager runs the durable harness for multi-agent, resumable, evidence-verified work.

Full mode treats the filesystem as durable task state and makes the manager responsible for convergence. Direct and Lite modes preserve the same bias toward real verification while avoiding process that does not help the current task.

It also avoids over-delegation: if the user asks for multi-agent execution on a tiny task, the manager first decides whether dispatch is actually useful. Small edits should be completed directly by one agent.

---

## User Benefits

### Resumable Long Tasks

Task state is written under `<project>/workspace/<task-slug>/`, so the manager can resume from previous specs, ledgers, reports, and handoffs.

### Cleaner Delegation

Each sub-agent gets bounded ownership: files, responsibility, expected report, evidence, and stop conditions.

### Evidence-Based Completion

Sub-agent completion is not final completion. The manager or evaluator verifies with tests, build output, browser checks, readback, logs, screenshots, or CI evidence.

For code behavior changes, the manager identifies the verification path before implementation. When meaningful tests exist or can be added at reasonable cost, workers should produce test-first evidence; docs-only and config-only work use proportionate substitute checks instead of meaningless tests.

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

Loading the skill does not mean dispatching agents or creating harness files. The manager first chooses the smallest mode that can handle the work:

- Use **Direct** for small edits, narrow local bugs, command output, copy changes, and single-agent fixes.
- Use **Lite** for medium work that benefits from decomposition, targeted review, or sequential subtask tracking, but does not need durable run artifacts.
- Use **Full** for independent ownership surfaces, real parallel workers, long or resumable scope, material verification risk, evaluator value, or isolation/rollback value.

Do **not** use it merely because a task is large. If the user has not authorized multi-agent execution, propose it briefly or proceed as a single agent.

---

## Operating Loop

```text
Context Intake
-> Mode Selection: Direct / Lite / Full
-> Execute the selected mode
   Direct: do the work, verify, report
   Lite: coordinate bounded slices, verify, report
   Full: run capability gate, acceptance registry, state machine, trace, and evaluator as needed
-> Merge / Handoff
```

The manager owns mode selection, scheduling when needed, merge, and final acceptance. Sub-agents are used only when they add value through parallelism, isolation, specialist review, or resumability.

## Full Harness Protocol

The full harness protocol is the stable core used only when Full mode is justified. It remains the same across runtimes.

### 1. Mode Selection Gate

Explicit multi-agent wording authorizes the manager to evaluate the mode; it does not force dispatch.

Full mode is justified when the task has independent ownership surfaces, long or resumable scope, material verification risk, evaluator value, or isolation/rollback value.

Full mode is not justified for typo fixes, small copy edits, direct commands, one-file changes, simple config tweaks, or narrow local bugs. In those cases the manager should use Direct mode, execute directly, and verify normally.

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

Create a clean runtime copy first:

```bash
python3 scripts/package_skill.py --output /tmp/multi-agent-dispatcher-runtime --force
```

Then install that clean copy:

```bash
mkdir -p ~/.codex/skills/multi-agent-dispatcher
rsync -a --delete /tmp/multi-agent-dispatcher-runtime/ ~/.codex/skills/multi-agent-dispatcher/
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
│   ├── superpowers-integration.md
│   └── stop-conditions.md
├── scripts/
│   ├── init_run.py
│   ├── package_skill.py
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

For Full mode artifact runs, initialize a run:

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

The Full Harness protocol is runtime-neutral. Adapters document the practical control points:

- where persistent instructions live
- how tools and sandbox limits are discovered
- how worktrees and file ownership are enforced
- whether browser verification is available
- how sub-agents or sequential fallbacks are represented
- how hooks or local instruction files preserve the protocol
- where trace and acceptance records should be written

Start with the adapter for the runtime you are actually using only after Full mode is selected. Direct and Lite mode should stay lightweight and use the runtime's ordinary verification path.

---

## Superpowers Integration

This project can borrow Superpowers-style methods, but does not require Superpowers to be installed.

Acknowledgement: this project is independent and intentionally borrows several engineering patterns inspired by [obra/superpowers](https://github.com/obra/superpowers), including test-first evidence, fresh-context subagents, review gates, worktree isolation, and verification-before-completion. It does not copy Superpowers skill bodies or require the Superpowers plugin to run.

The relationship is:

```text
multi-agent-dispatcher = routing authority
Superpowers-style methods = optional supporting methods
```

Mode Selection always runs first. A small task stays Direct even if TDD, worktree, review, or parallel-agent skills are available. Lite and Full modes can borrow the useful methods when they reduce risk:

- independent problem-domain splitting
- fresh task-local worker prompts
- test-first evidence for code behavior changes
- separate spec compliance and code quality review
- worktree isolation for conflict-prone parallel edits
- verification before completion

See [`references/superpowers-integration.md`](references/superpowers-integration.md).

## Sharing The Skill

Share the repository or a clean package containing the runtime skill files:

- `SKILL.md`
- `master-prompt.md`
- `sub-prompt.md`
- `agents/openai.yaml`
- `adapters/`
- `references/`
- `templates/`
- `scripts/init_run.py`
- `scripts/validate_report.py`

Keep human-facing docs such as this `README.md` and packaging helpers such as `scripts/package_skill.py` at the repo/package level. Do not include local memories, generated task workspaces, session logs, caches, bytecode, personal config, credentials, or `.git` internals in an installed runtime copy.

---

## v5.2.1 Highlights

- Added explicit acknowledgement that the design borrows engineering patterns inspired by `obra/superpowers`.
- Tightened `SKILL.md` frontmatter so it describes trigger conditions instead of summarizing workflow.
- Added `scripts/package_skill.py` to create a clean runtime-only copy for sharing or installation.

## v5.2.0 Highlights

- Added Superpowers-aware routing while keeping `multi-agent-dispatcher` as the single entrypoint.
- Added testing and review gates for Lite/Full code behavior changes.
- Added fresh-context worker guidance and stricter independent-domain dispatch criteria.
- Added sharing/package guidance to keep runtime installs lean and portable.
- Added eval cases for TDD evidence, two-stage review, Superpowers interaction, and clean sharing.

## v5.1.0 Highlights

- Added three-mode routing: **Direct**, **Lite**, and **Full**.
- Made Full Harness explicitly on-demand instead of the default path for every request.
- Reduced overproduction of artifacts for small and medium tasks.
- Aligned the public guidance with Codex and Claude community practice: less ceremony, real verification, and sub-agents only when they add value.

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

v5.2 keeps the public skill purpose the same, but makes the manager choose the smallest useful mode first and borrow mature supporting methods only when they fit the selected mode:

- Treat multi-agent work as a protocol run only when Full mode is justified.
- Prefer Direct or Lite mode when full artifacts would add overhead without improving verification.
- Use Superpowers-style TDD, review, worktree, verification, and parallel-agent methods as supporting controls, not as a competing top-level router.
- Record actual runtime capabilities before dispatching workers.
- Keep acceptance criteria in `acceptance_registry.json` and require evidence before completion.
- Keep run progress in `run_state.json`, `progress.md`, and `trace.jsonl` so another manager can resume.
- Use runtime adapters only to map the same protocol onto Codex, Claude Code, or similar harnesses.

Existing v4 and v5 prompts and templates still map cleanly to v5.2, but long or risky tasks should use Full mode and the full artifact set.

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

**v5.2.1** · 2026-05-28

Previous public release: **v5.0.1** · 2026-05-27
