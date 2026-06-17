# Ingest Meeting Transcripts

Use when ingesting meeting transcriptions into Joshua's business and personal master prompts in Notion. Runs automatically via scheduled agent at 4:30 PM daily, or manually when a specific transcript needs processing.

---

## What This Skill Does

1. Finds all new Notion meeting transcripts from today (any meeting, any participant)
2. Extracts structured context from each transcript
3. Classifies each insight as Personal, Business (Big Picture), or Business (Current Priorities)
4. Updates the correct Notion master prompt sections
5. Flags anything worth adding to CLAUDE.md

---

## Step 1 — Find Today's Transcripts

Search Notion for all meeting transcripts from today:

```
Search query: "Meeting" with today's date
Filter: pages created or modified today
Include: Morning meetings, tenant meetings, investor meetings, vendor calls, any other meetings
```

Use `notion-search` with today's date. If no new transcripts exist, log "No new transcripts found for [date]" and stop.

---

## Step 2 — Extract From Each Transcript

For each transcript, extract:

**Decisions made** — anything resolved, agreed on, or committed to
**Action items** — who is doing what by when
**Property updates** — any news on specific addresses (repairs, payments, tenants, deals)
**People mentioned** — new contacts, existing team/tenant/vendor updates
**Business priorities** — what's moving up or down the stack
**Personal observations** — language patterns, preferences stated, frustrations expressed, how Joshua responded to things
**New context** — anything not already in the master prompts (new deal, new tool, new SOP, new relationship)

---

## Step 3 — Classify Each Insight

Before writing anything, classify every extracted item:

| Type | Goes To |
|---|---|
| Communication style, tone, language, habits, personal preferences, behavioral patterns | Personal Master Prompt |
| Entities, team updates, property updates, deals, vendors, tools, SOPs | Business — Big Picture |
| Active tasks, recent decisions, current priorities, what's shifting this week | Business — Current Priorities |

When an insight touches both personal and business, update both.

---

## Step 4 — Update Notion

**Business Master Prompt — Current Priorities section:**
- Replace (don't append) with a fresh summary of what's active right now
- Format: date header + bullet points, grouped by category (Properties, Active Projects, Decisions Made, Action Items, People)
- Keep it tight — max 30 bullets

**Business Master Prompt — Big Picture section:**
- Only update when something structural changed (new entity, team change, new property, new tool added to stack)
- Never overwrite stable facts with meeting chatter

**Personal Master Prompt:**
- Append new behavioral observations under a new dated section (like Section 13/14 already in the prompt)
- Only add if genuinely new — don't duplicate what's already there

Notion pages:
- Personal: https://www.notion.so/36692db18570812cb5d7c01bae307e4a
- Business: https://www.notion.so/36692db1857081739b02dd7e3c8a44d7

---

## Step 5 — Flag for CLAUDE.md

After updating Notion, check if anything extracted should also be reflected in CLAUDE.md:
- New non-negotiable preference → add to Communication Style or What Frustrates Him
- New active project → update What He's Building Right Now
- Structural business change → update My Business section

Output a summary of what was updated and what (if anything) needs to be synced to CLAUDE.md. Do not update CLAUDE.md automatically — surface it for Joshua to confirm.

---

## Output Format

After completing ingestion, report:

```
Transcripts processed: [n] — [list of meeting titles]
Personal updates: [what was added/observed]
Business (Big Picture) updates: [what changed structurally]
Business (Current Priorities): [refreshed summary]
CLAUDE.md sync needed: [yes/no — what specifically]
```
