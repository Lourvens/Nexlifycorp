# Task Progression Rules

Rules for tracking long-running agent tasks across multiple concurrent harness executions. See `PROGRESSION.md` for the live task log.

## Purpose

When running multiple agents concurrently (via harness, loop, or parallel tasks), it's easy to lose track of which agent is working on what, what's blocked, and where it stands. `PROGRESSION.md` provides a shared scratch pad for that context.

## Status Definitions

- **pending**: Queued, not yet started
- **in_progress**: Active work, not blocked
- **blocked**: Waiting on input, dependencies, or decisions from human
- **completed**: Done, task fulfilled
- **stuck**: Agent hit an error or dead-end, needs human intervention

Status lifecycle: `pending` → `in_progress` → `blocked`/`completed`/`stuck`

## Usage

- Update `PROGRESSION.md` when starting a task, when status changes, or when you observe something notable
- Find active tasks: `grep -E "(in_progress|blocked|stuck)" PROGRESSION.md`
- Completed tasks can be left in place (acts as history) or moved to an `# Archive` section at the bottom
- This is a context scratch pad for complex multi-agent sessions — not a substitute for proper project tracking

## Task Entry Format

```markdown
## [YYYY-MM-DD HH:mm] TASK TITLE

**Agent**: <agent-name> | <task-id if any>
**Status**: <pending|in_progress|blocked|completed|stuck>
**What's happening**: Brief description of current step
**Blockers**: None | <what's blocking>
**Updated**: <timestamp>
**Notes**: <optional observations, decisions made, things to revisit>
```