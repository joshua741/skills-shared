---
name: agent-teams
description: Use when spinning up, managing, or troubleshooting an agent team — multiple Claude instances coordinating on complex parallel work. Covers when to use teams vs subagents, how to spawn and structure a team, task sizing, and common failure patterns.
argument-hint: [what you want the team to do]
---

# Agent Teams

Read the full reference before doing anything: `~/.claude/skills/agent-teams/reference.md`

## When a Team Is the Right Call

Use an agent team when:
- Work splits cleanly into parallel tracks with distinct file ownership
- Teammates need to share findings and challenge each other (not just report back)
- You want competing hypotheses on a bug or design problem simultaneously

Use subagents instead when:
- Workers only need to report a result back — no peer communication needed
- Tasks are sequential or heavily dependent on each other
- Same files are being edited (two teammates on the same file = overwrites)

## Spawning a Team

Just describe what you want in natural language:

```
Create an agent team to review PR #142.
Spawn three reviewers: one on security, one on performance, one on test coverage.
```

Claude creates the team, assigns tasks, and coordinates via a shared task list.

## Key Rules

- **Name teammates explicitly** — predictable names make targeting reliable
- **One file owner per teammate** — no shared file editing
- **5–6 tasks per teammate** keeps everyone productive
- **Start with 3–5 teammates** — coordination overhead grows with team size
- **Include context in spawn prompts** — teammates don't inherit conversation history
- **Clean up when done** — "Clean up the team" from the lead, after all teammates shut down

## Controls

| Action | How |
|---|---|
| Cycle through teammates | Shift+Down |
| Message a teammate | Shift+Down → type |
| View a teammate's session | Enter |
| Interrupt | Escape |
| Toggle task list | Ctrl+T |
| Shut down one teammate | "Ask the [name] teammate to shut down" |
| Clean up the team | "Clean up the team" (from lead) |

## Require Plan Approval Before a Teammate Acts

```
Spawn an architect teammate to refactor the auth module.
Require plan approval before they make any changes.
```

Lead reviews plan → approves or rejects → teammate implements only after approval.

## If $ARGUMENTS Were Provided

Spin up a team to accomplish: $ARGUMENTS

Design the team structure (how many teammates, what each owns) before spawning. Reference the full doc for team size guidance and task sizing rules.
