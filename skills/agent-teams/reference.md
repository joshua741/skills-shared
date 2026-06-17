# Agent Teams — Master Reference Guide

Source: https://code.claude.com/docs/en/agent-teams  
Requires: Claude Code v2.1.32+, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## What Agent Teams Are

Multiple Claude Code instances coordinating as a team. One session is the **lead** — it creates the team, spawns teammates, assigns tasks, and synthesizes results. Teammates are fully independent sessions with their own context windows and can message each other directly.

Unlike subagents (which only report back to the calling agent), teammates communicate peer-to-peer.

---

## Enable

Already set in `settings.local.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## Subagents vs. Agent Teams

| | Subagents | Agent Teams |
|---|---|---|
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Report to main agent only | Message each other directly |
| Coordination | Main agent manages all work | Shared task list, self-coordinating |
| Best for | Focused tasks, result only matters | Complex work needing discussion |
| Token cost | Lower | Higher (each teammate = full Claude instance) |

**Rule of thumb:** Use subagents when workers only need to report back. Use agent teams when teammates need to share findings, challenge each other, and self-coordinate.

---

## When to Use Agent Teams

**Strong use cases:**
- Research/review from multiple angles simultaneously
- New modules/features where teammates each own separate files
- Debugging with competing hypotheses (teams converge faster)
- Cross-layer changes (frontend, backend, tests — each owned by a different teammate)

**Avoid for:** Sequential tasks, same-file edits, heavily dependent work — single session or subagents are more efficient.

---

## Starting a Team

Just tell Claude what you want in natural language:

```
Create an agent team to explore this CLI tool from different angles:
one teammate on UX, one on technical architecture, one playing devil's advocate.
```

Claude creates the team, spawns teammates, and coordinates via a shared task list. The lead's terminal lists all teammates. Use **Shift+Down** to cycle through them.

---

## Architecture

| Component | Role |
|---|---|
| Team lead | Main session — creates team, spawns teammates, coordinates |
| Teammates | Separate Claude instances working assigned tasks |
| Task list | Shared work items; teammates claim and complete them |
| Mailbox | Messaging system for inter-agent communication |

**Storage (auto-generated, do not edit by hand):**
- Team config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`

The `config.json` `members` array holds each teammate's name, agent ID, and agent type — teammates read this to discover each other.

---

## Display Modes

### in-process (default when not in tmux)
All teammates run inside your main terminal. Use **Shift+Down** to cycle through, type to message them. Works in any terminal.

### tmux / split panes (default when already in tmux)
Each teammate gets its own pane. See all output at once, click into panes to interact directly. Requires tmux or iTerm2 with `it2` CLI.

**Override in `~/.claude/settings.json`:**
```json
{ "teammateMode": "in-process" }
```

**Override for a single session:**
```bash
claude --teammate-mode in-process
```

**Install tmux:** via system package manager. **Install it2:** `npm install -g it2`, then enable Python API in iTerm2 → Settings → General → Magic.

---

## Control Reference

### Specify teammates and models
```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```
Teammates don't inherit the lead's model by default. Set **Default teammate model** in `/config` to change the default.

### Require plan approval before a teammate acts
```
Spawn an architect teammate to refactor the auth module.
Require plan approval before they make any changes.
```
Lead reviews plan → approves or rejects with feedback → teammate implements only after approval.

### Talk to a teammate directly
- **in-process**: Shift+Down to cycle, type to send, Enter to view session, Escape to interrupt
- **split-pane**: click the pane

### Shut down a specific teammate
```
Ask the researcher teammate to shut down
```
Teammate can approve (graceful exit) or reject with explanation.

### Clean up the team
```
Clean up the team
```
Always run from the lead. Shut down all teammates first — cleanup fails if active teammates exist.

---

## Task System

Tasks have three states: **pending → in progress → completed**. Tasks can have dependencies; a task cannot be claimed until its dependencies are complete.

- **Lead assigns**: tell the lead which task to give which teammate
- **Self-claim**: teammates pick up the next unassigned, unblocked task after finishing one
- **File locking** prevents race conditions when multiple teammates try to claim the same task

---

## Context & Communication

- Teammates load: CLAUDE.md, MCP servers, skills (from project/user settings)
- Teammates do NOT inherit: lead's conversation history
- Message delivery is automatic — lead doesn't poll
- Idle notification: teammate auto-notifies lead when it stops
- To message everyone: send one message per recipient (no broadcast)
- Lead assigns each teammate a name at spawn — name them explicitly for predictable targeting

---

## Subagent Definitions as Teammates

You can reference a named subagent type when spawning a teammate:

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

The teammate gets the subagent's `tools` allowlist and `model`, and the definition's body is appended to the teammate's system prompt (not replacing it). Team coordination tools (`SendMessage`, task tools) are always available regardless of `tools` restrictions.

**Note:** `skills` and `mcpServers` frontmatter in subagent definitions are NOT applied when running as a teammate — those load from project/user settings instead.

---

## Hooks for Quality Gates

| Hook | Trigger | Use |
|---|---|---|
| `TeammateIdle` | Teammate about to go idle | Exit code 2 to keep them working |
| `TaskCreated` | Task being created | Exit code 2 to block creation |
| `TaskCompleted` | Task being marked complete | Exit code 2 to block completion |

---

## Permissions

- Teammates inherit the lead's permission settings at spawn time
- If lead uses `--dangerously-skip-permissions`, all teammates do too
- Can change individual teammate modes after spawning
- Cannot set per-teammate modes at spawn time

---

## Token Cost

Each teammate = a full independent Claude instance. Costs scale linearly with teammates. Factor this into team size decisions — see `/en/costs#agent-team-token-costs`.

---

## Best Practices

### Team size
- **Start with 3–5 teammates** for most workflows
- 5–6 tasks per teammate keeps everyone productive
- Scale up only when parallel work genuinely helps — 3 focused teammates often beat 5 scattered ones
- Beyond a certain point, coordination overhead exceeds benefit

### Task sizing
- Too small: coordination overhead kills the benefit
- Too large: teammates run too long without check-ins, wasted effort risk
- Right size: self-contained units with a clear deliverable (a function, a test file, a review)

### Context in spawn prompts
Include task-specific details — teammates don't inherit conversation history:

```
Spawn a security reviewer with this prompt: "Review src/auth/ for vulnerabilities.
Focus on token handling, session management, input validation. App uses JWT in
httpOnly cookies. Report issues with severity ratings."
```

### Avoid file conflicts
Each teammate should own distinct files. Two teammates editing the same file = overwrites.

### Keep the lead from jumping in
If the lead starts implementing instead of delegating:
```
Wait for your teammates to complete their tasks before proceeding
```

### Monitor and steer
Check in on progress, redirect failing approaches early, synthesize findings as they arrive. Don't let teams run unattended too long.

### Start with research/review tasks
Best first use: PR review, library research, bug investigation — clear boundaries, no parallel write conflicts.

---

## Use Case Patterns

### Parallel code review (domain separation)
```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
```

### Competing hypothesis debugging
```
Users report the app exits after one message. Spawn 5 teammates to investigate
different hypotheses. Have them debate and try to disprove each other's theories.
Update the findings doc with whatever consensus emerges.
```

### Multi-perspective design exploration
```
I'm designing a CLI tool for tracking TODO comments. Create an agent team:
one teammate on UX, one on technical architecture, one playing devil's advocate.
```

---

## Limitations (Experimental)

| Limitation | Workaround |
|---|---|
| No session resumption for in-process teammates | After `/resume`, spawn new teammates |
| Task status can lag (blocking dependents) | Manually update status or nudge via lead |
| Shutdown can be slow (finishes current call first) | Be patient; check status with Shift+Down |
| One team at a time per lead | Clean up before creating a new team |
| No nested teams (teammates can't spawn teams) | Only lead manages the team |
| Lead is fixed for team lifetime | Can't promote teammates or transfer leadership |
| Split panes require tmux or iTerm2 | Use in-process mode in VS Code, Windows Terminal, Ghostty |

---

## Troubleshooting

**Teammates not appearing:**
- In-process: press Shift+Down to cycle — they may already be running
- Check task complexity — Claude may not have spawned a team if task seemed simple
- Verify `which tmux` if split-pane was requested

**Too many permission prompts:**
Pre-approve common operations in permission settings before spawning teammates.

**Teammate stopped on error:**
Use Shift+Down to read output, then give direct instructions or spawn a replacement.

**Lead shuts down early:**
Tell it to keep going, or pre-instruct it to wait for teammates.

**Orphaned tmux sessions:**
```bash
tmux ls
tmux kill-session -t <session-name>
```

---

## Quick Reference Card

```
Enable:           CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
Spawn team:       "Create an agent team with X teammates to..."
Cycle teammates:  Shift+Down
Message teammate: Shift+Down then type
Interrupt:        Enter (view session) → Escape
Toggle task list: Ctrl+T
Shut down one:    "Ask the [name] teammate to shut down"
Clean up:         "Clean up the team" (from lead, after all shutdown)
Force in-process: claude --teammate-mode in-process
```
