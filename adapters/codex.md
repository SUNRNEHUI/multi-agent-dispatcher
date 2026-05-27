# Codex Runtime Adapter

This adapter maps the v5 harness protocol onto Codex-style runtimes. It is not a feature comparison; it is a checklist of practical control points the manager must use or explicitly mark unavailable.

## Persistent Instructions

Use the most specific instruction source available:

- user-level and workspace `AGENTS.md`
- project-level `AGENTS.md`
- installed skills and their references
- task-specific artifacts under the active project

Project rules override broader rules when they conflict. The manager should read the relevant files before editing and record any protocol-relevant constraints in the trace.

## Right-Sizing Gate

In Codex, skill loading and actual dispatch are separate decisions. If the user mentions multi-agent work for a tiny edit, use the skill to decide that dispatch is unnecessary, then complete the task directly. Do not spawn workers, create worktrees, or initialize artifact directories unless delegation is justified.

## Capability Gate

Record the actual session capabilities before dispatch:

- writable paths and explicit user write limits
- shell availability and sandbox policy
- network availability
- browser or app automation tools
- image, document, spreadsheet, or other specialized tools if relevant
- whether real sub-agent delegation exists in the active environment
- whether worktrees are safe given current git status

If real sub-agents are unavailable, run sequential worker stages and say so in the trace. Do not label sequential work as parallel execution.

## Filesystem And Sandbox

Codex work is usually grounded in the local workspace. The manager should:

- inspect `git status` before edits
- avoid reverting unknown user changes
- keep writes inside the user's authorized file set
- use worktrees only when the repository state and task split justify them
- write durable run state to the project workspace or another user-approved artifact path

Sandbox and approval limits are part of the capability record. Missing permission is a stop or fallback, not a reason to fabricate evidence.

## Tools And Browser Verification

Browser verification is required for meaningful UI acceptance when a browser tool is available and the task touches user-facing web behavior. If it is unavailable, the manager records the limitation and either uses a narrower check or asks for a decision when the gap affects acceptance.

Shell commands, tests, builds, logs, screenshots, API readbacks, and browser interactions can all become acceptance evidence, but only if the trace records what was checked.

## Sub-Agents And Workers

When Codex has a real delegation mechanism, each worker should receive:

- bounded goal
- allowed paths or responsibility surface
- required report path
- required evidence
- stop conditions
- four-line return contract

When it does not, the manager can still run the same protocol with sequential stages. The state machine should show the fallback so later readers know no parallel isolation occurred.

## Hooks And Skills

Skills provide workflow instructions and reusable references. They should not be treated as proof that a capability exists. A skill can tell the manager how to run the harness; the capability gate still decides what can actually be done in the current session.

Hooks, if present in the local setup, are useful for recording or enforcing protocol state, but the manager should not depend on unverified hooks for acceptance. Critical acceptance evidence must be visible in durable artifacts.

## Trace Placement

For complex runs, keep trace in the progress ledger or a dedicated trace file under the task artifact directory. Minimum trace entries:

- capability gate result
- state transitions
- worker or sequential-stage report paths
- evaluator result
- acceptance registry status
- budget breaker events

The final response should summarize evidence, not replace the trace.
