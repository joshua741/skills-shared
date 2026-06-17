---
name: session-handoff
description: >
  Generates a comprehensive handoff prompt so the user can continue a conversation in a new session without losing context. Use this skill whenever the user says things like "give me a prompt to continue this," "create a handoff prompt," "I want to resume this conversation," "make a prompt for another Claude," "continue in a new session," "save my place," or "I need to start over with full context." Also trigger when the user asks for a "continuation prompt," "resume prompt," or says they want to "pick up where we left off" in a new chat. Always use this skill proactively when the user is wrapping up a long work session involving files, code, or multi-step tasks.
---

# Session Handoff Skill

Your job is to produce a single, self-contained prompt the user can paste into a new conversation to resume exactly where they left off. Think of it as writing a thorough briefing for a smart colleague who just walked in with no context.

## What makes a great handoff prompt

A great handoff prompt gives the new Claude everything it needs to act immediately — without asking clarifying questions. It should read like a smart human handed off a project, not like a log dump. The new Claude needs to understand:

- Who the user is and what they're trying to accomplish overall
- What has already been done (specific outputs, decisions, file locations)
- What the exact next steps are
- What open questions or blockers exist
- Any key rules, preferences, or corrections the user established during the session (these are gold — don't lose them)

## How to build it

**Step 1 — Scan the conversation**
Read back through the full conversation and identify:
- The user's name and role (if known)
- The core goal of the session
- Every significant output created (files, documents, code, reports) — include exact file paths
- Key decisions or corrections the user made that changed the approach
- Work that was started but not finished
- Open questions that need answers
- Tools, MCPs, or integrations that were actively used

**Step 2 — Check for summary files**
Look in the workspace folder for any session summary, tracker, or notes file that was created. Read it if it exists — it may contain structured information that complements what you found in the conversation.

**Step 3 — Write the prompt**

Structure it like this:

```
## Who I am
[Name, role, business context — 2-3 sentences]

## What we were working on
[Plain English description of the project/task — 1 paragraph]

## What has already been done
[Bullet list of completed work with file paths where relevant]

## Key rules and corrections established
[Bullet list of any preferences, corrections, or constraints the user set during the session — this is critical]

## What needs to happen next
[Numbered list of specific next steps in priority order]

## Open questions I need to answer
[Numbered list of things the user still needs to provide or decide]

## Files and locations
[List of all relevant file paths]

## How to start
[One clear instruction for what to do first when you receive this prompt]
```

## Style guidelines

- Write the prompt in first person from the user's perspective ("I am...", "We were working on...", "I need you to...")
- Be specific — file paths, dollar amounts, property addresses, entity names, etc. Generic language wastes the new Claude's time
- Include the key corrections the user made during the session. If they said "don't do X" or "actually it works this way," that must survive the handoff
- Keep it tight. The goal is density of useful information, not completeness for its own sake. The new Claude can always ask follow-up questions; what it can't do is recover context that was never provided.

## Output format

Deliver the handoff prompt inside a clearly labeled code block so the user can copy it easily:

```
---COPY FROM HERE---

[the full prompt]

---END---
```

After the code block, add a brief note explaining what the new Claude should be able to do immediately with this prompt, and what it will still need from the user (if anything).
