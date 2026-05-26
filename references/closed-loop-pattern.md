# Closed Loop Pattern

Long-running multi-agent work fails most often through state drift, planning drift, shallow verification, ownership conflicts, and false completion. Keep the loop small and evidence-driven.

## Five Control Layers

1. **State**
   Durable task state lives outside chat: goal, progress, changed files, decisions, verification, open risks, blockers, and next step.

2. **Planning**
   The plan is a job spec, not a motivational checklist. It defines stage boundaries, inputs, outputs, verification, budget, and stop conditions.

3. **Execution**
   Tool calls and sub-agent results must return to state. File edits, command results, browser findings, API calls, and decisions should be summarized in the ledger when they matter for continuation.

4. **Verification**
   Completion requires evidence. Tests, builds, screenshots, database readback, logs, CI, and evaluator reports are stronger than the executor saying the work is done.

5. **Supervision**
   The system must know when to stop: scope growth, budget pressure, repeated failures, destructive actions, release/publish steps, paid APIs, permissions, production data, or ownership conflicts.

## Practical Patterns

- **Spec-first:** clarify goal, non-goals, constraints, acceptance criteria, and risk before large execution.
- **Plan gate:** review the task split before work accelerates; a bad split compounds quickly.
- **Progress ledger:** update durable state after each meaningful stage.
- **Sub-agent reports:** keep chat short and move detail into files.
- **Independent evaluator:** separate generation from final judgment for high-risk or user-facing work.
- **Browser-level verification:** web products must be clicked and inspected, not only checked by curl or unit tests.
- **Rollback path:** preserve a way back before high-impact operations.
- **Trace important steps:** keep enough evidence to answer why a decision was made and how completion was verified.
