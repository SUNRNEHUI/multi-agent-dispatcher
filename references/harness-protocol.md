# Harness Protocol Reference

This reference defines the v5 core protocol. It is intentionally separate from any one agent runtime. Runtime adapters may become thinner as models improve, but the manager still needs a durable protocol for state, evidence, budget, and final acceptance.

## Protocol Goal

The harness turns multi-agent orchestration from advice into a required control loop:

1. discover actual runtime capabilities
2. create a bounded spec and acceptance registry
3. advance through explicit states
4. collect worker and evaluator evidence
5. stop on budget or safety breaks
6. claim completion only when required acceptance records pass

## Required Records

A run should preserve these records in durable files when the task is complex or resumable.

### Capability Record

- runtime name
- available tools
- unavailable tools
- filesystem and sandbox limits
- browser or UI verification availability
- sub-agent mechanism or fallback
- worktree support
- external dependencies and credentials
- chosen fallback for missing capabilities

### State Record

- current state
- previous state
- transition reason
- owner
- timestamp or ordering marker
- evidence path
- next action

### Acceptance Record

- criterion
- owner
- required evidence
- status: `pending`, `pass`, `fail`, `blocked`, or `scoped_out`
- evidence path or command summary
- evaluator notes when relevant

### Budget Record

- stage budget
- observed usage
- breaker condition
- stop reason
- continuation decision

### Trace Record

- capability gate result
- dispatch decisions
- report paths
- evaluator result
- commands or checks that matter for acceptance
- final registry status

## State Machine

Use these states as the default harness model:

```text
INTAKE
GATED
SPECIFIED
DISPATCHED
REPORTED
EVALUATING
ACCEPTED
HANDED_OFF
```

Stop states:

```text
BLOCKED
NEEDS_DECISION
FAILED
```

The manager may use fewer states for a small delegated task, but it must not skip the gate, acceptance, and final verification semantics.

## Completion Rule

The manager can say the task is complete only when:

- required capability fallbacks are recorded
- every required acceptance record is `pass` or explicitly `scoped_out` by user decision
- evaluator `FAIL` has been resolved or explicitly scoped out by user decision
- budget breakers are closed with a continuation or stop decision
- trace points to the evidence used for completion

Worker success is not completion. A worker report is input to acceptance, not the acceptance decision itself.

## What Gets Thinner As Models Improve

These layers can shrink over time because stronger models can infer or execute them with less scaffolding:

- verbose prompt wording
- role descriptions repeated in every task
- manual checklists for obvious file ownership
- adapter-specific reminders about basic tool use
- large chat summaries when durable trace exists
- evaluator rubrics for low-risk, narrow edits

The direction is thinner instructions, not weaker guarantees.

## What Remains Long-Term

These layers should remain even with stronger models:

- capability gate: the runtime environment can change independently of the model
- state machine: long tasks need resumable state
- acceptance registry: completion needs evidence tied to criteria
- budget circuit breaker: cost, time, context, and retries remain finite
- trace: future agents need to know what happened and why
- stop conditions: destructive or high-impact operations still need explicit control
- runtime adapters: harness controls differ across products and local setups

## Adapter Contract

Each runtime adapter should answer:

- where persistent instructions live
- how capabilities are discovered
- how filesystem, sandbox, and network limits are represented
- how worktree or file ownership can be enforced
- how browser verification is performed or marked unavailable
- how sub-agents are launched, simulated, or replaced by sequential stages
- how hooks or local instructions preserve the protocol
- where trace and acceptance records should be written

Adapters must avoid claiming unavailable features. Missing controls should become fallbacks or stop conditions.
