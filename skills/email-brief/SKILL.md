---
name: email-brief
description: Use when asked to run the email brief, process the inbox, run email intelligence, generate the morning briefing, generate the afternoon briefing, or check what happened in email. Reads joshua@webberinvestmenthomes.com, triages every unread email, matches emails to Notion tasks, drafts replies, detects new tasks, updates master prompts, and writes the complete briefing to Notion.
disable-model-invocation: true
argument-hint: [morning | afternoon]
context: fork
---

## What This Skill Does

Runs the Email Intelligence process for Joshua Webber. Every run produces a pre-digested briefing written into the Notion daily task page. The briefing tells Joshua what happened in his inbox, what it means for open tasks, what to say back, and what new work it implies.

This is not a generic summarizer. It is a task-aware, deal-aware, contact-aware intelligence layer. Every email surfaced must answer: **does this move the needle on something Joshua is already working on, or does it create something new he needs to know about?** Emails that do neither are auto-handled invisibly.

See supporting files for detailed rules:
- `triage-rules.md` — the three filters, tier definitions, sender classification
- `output-format.md` — exact Notion digest format and section layout
- `reply-style.md` — reply draft voice and non-negotiable style rules
- `living-context-store.json` — persistent Living Context Store (read and write this file directly)

---

## Critical Account Specifications

These are non-negotiable. Every connection made must point to the correct account. Never default to any other inbox or workspace.

**Gmail:** `joshua@webberinvestmenthomes.com` — only this inbox. Never `webberinvestmenthomes@gmail.com` or any other address.

**GoHighLevel:** Business = Webber Wealth Holdings | Location ID = `EKfRUZkioMTfy1vtYvua` — only this location. All contact lookups, pipeline reads, tag reads, and internal note reads happen inside this location exclusively.

**Notion — Business Master Prompt:** `https://www.notion.so/36692db185708164a179f46cf8272c78`

**Notion — Personal Master Prompt:** `https://www.notion.so/36692db18570815b965ef33f42bb5547`

---

## Run Schedule

- **Morning run: 9:15 AM CT** — covers all unread email from the past 18 hours. Briefing ready before Joshua's 9:30 AM email block.
- **Afternoon run: 4:45 PM CT** — covers all unread email since the morning run. Does not re-surface items already shown in the morning briefing that are resolved or acknowledged.

If  is `morning`, run morning mode. If `afternoon`, run afternoon mode. If omitted, infer from current time.

---

## Full Process — Run in This Exact Order

### Step 0 — Read Context

Read all context sources before processing a single email. This order is mandatory.

1. **Read Suggestions** from the Notion daily page. For each suggestion Joshua left:
   - Apply it immediately to this run
   - Write it permanently to the Living Context Store
   - If it belongs in a master prompt, write it there now (additive, dated, no overwrites)
   - Mark it `✓ Added — [date]` so Joshua sees it was absorbed
   - Schedule it for clearing on the next run

2. **Read Business Master Prompt** from Notion: `https://www.notion.so/36692db185708164a179f46cf8272c78`

3. **Read Personal Master Prompt** from Notion: `https://www.notion.so/36692db18570815b965ef33f42bb5547`

4. **Read full Notion daily task page** — never cached, always live. Extract: open tasks, needle mover task, delegate assignments, deal references, property addresses, contact names, priorities.

5. **Read Living Context Store** — read `C:\Users\joshu\.claude\skills\email-brief\living-context-store.json` in full. This is the authoritative internal knowledge base for this run.

6. **Query GHL** (`EKfRUZkioMTfy1vtYvua`) for current pipeline state on all active deals. Update Living Context Store.

### Step 1 — Process Inbox

1. Fetch all unread emails from `joshua@webberinvestmenthomes.com` since the last run.
2. Score each email against the three filters (see `triage-rules.md`).
3. For any sender not already fully classified in the Living Context Store, query GHL (`EKfRUZkioMTfy1vtYvua`) by email address first, then by name. Store classification result permanently.
4. Assign triage tier (1, 2, or 3) to every email.
5. Auto-handle all Tier 3 emails: mark read, log sender and subject to Living Context Store. Never show in briefing.
6. Update Living Context Store with any new contact, deal, or relationship intelligence learned from this batch.

### Step 2 — Needle Mover Check

Identify today's needle mover task from the Notion task page. Cross-reference all Tier 1 and Tier 2 emails against it. Any match gets promoted to the top of the briefing with a `🎯 NEEDLE MOVER MATCH` flag, regardless of all other scoring.

### Step 3 — Task Matching

For each Tier 1 and Tier 2 email: read the full open task list and identify which specific Notion task(s) the email is relevant to. Matching is contextual and relational — not keyword-only. One email can match multiple tasks. Record the exact task name.

### Step 4 — New Task Detection

For each Tier 1 and Tier 2 email: identify any implied work not already on the task list. Draft suggested new tasks with description, priority level (P1–P7), and routing/delegate. Write confirmed new tasks directly to the appropriate Notion section. Log each new task added.

### Step 5 — Reply Draft Generation

For every Tier 1 email where a reply would move a task forward: generate a complete reply draft written in Joshua's voice. Use the Personal Master Prompt as the voice reference. Use deal and task context as the content reference. See `reply-style.md` for mandatory style rules.

### Step 6 — Update Master Prompts

Review what was learned this run. If any insight belongs permanently in the Business or Personal Master Prompt, write it now:
- Format: `[Month Day, Year — Auto-updated by Email Intelligence Skill] [insight]`
- Additive only — never overwrite or delete existing content
- If something in a master prompt appears outdated, append: `[Date — Note: this section may need review based on recent correspondence]`

### Step 7 — Write Briefing to Notion

Write the complete email briefing to the `EMAIL BRIEFING` section of the Notion daily page, positioned directly below TODAY'S MEETINGS. Clear any Suggestions that were marked `✓ Added` in the prior run. Follow the exact format in `output-format.md`.

---

## The Living Context Store

**File:** `C:\Users\joshu\.claude\skills\email-brief\living-context-store.json`

The Living Context Store is the skill's internal brain — a persistent, self-updating knowledge base stored as a local JSON file. It is never shown to Joshua in full. Read it at the start of every run (Step 0). Write updates to it throughout the run as new intelligence is learned. Never require manual maintenance.

**Top-level keys and their schemas:**

`_meta` — run metadata
```json
{
  "version": "1.0",
  "last_updated": "ISO 8601 datetime",
  "last_run": "ISO 8601 datetime",
  "last_run_type": "morning | afternoon",
  "total_runs": 0
}
```

`contact_intelligence.contacts` — keyed by email address
```json
{
  "email@example.com": {
    "name": "Full Name",
    "phone": "string or null",
    "role": "deal contact | team member | financial platform | title | lender | contractor | vendor | tenant | prospect | unknown",
    "deal_associations": ["4412 Birchwood", "..."],
    "ghl_contact_id": "string or null",
    "ghl_pipeline_stage": "string or null",
    "ghl_tags": [],
    "ghl_notes_summary": "string or null",
    "last_seen": "ISO 8601 datetime",
    "first_seen": "ISO 8601 datetime"
  }
}
```

`deal_intelligence.deals` — keyed by property address
```json
{
  "4412 Birchwood St": {
    "deal_type": "RTO | seller finance | transactional lending | subject-to | wholesale",
    "status": "active | pending | closed | dead",
    "key_contacts": ["email@example.com"],
    "open_task_names": ["exact Notion task name"],
    "financial_figures": { "purchase_price": 287500, "arv": null },
    "last_updated": "ISO 8601 datetime"
  }
}
```

`sender_classification_registry.senders` — keyed by email address or domain (`@domain.com`)
```json
{
  "alerts@baselane.com": {
    "display_name": "Baselane",
    "classification": "financial platform",
    "default_tier": 1,
    "tier_rules": [
      { "condition": "account activity", "tier": 1 },
      { "condition": "promotional", "tier": 3 }
    ],
    "classified_on": "ISO 8601 datetime",
    "classification_source": "auto | suggestion"
  }
}
```

`learned_routing_rules.rules` — array of inferred routing preferences
```json
[
  {
    "rule": "Tasks involving seller finance docs route to Joshua directly",
    "source": "suggestion | inferred",
    "learned_on": "ISO 8601 datetime"
  }
]
```

`active_pipeline_context.pipelines` — GHL pipeline state, refreshed every run
```json
[
  {
    "pipeline_name": "string",
    "pipeline_id": "string",
    "stages": [
      {
        "stage_name": "string",
        "contacts": [
          { "name": "string", "email": "string", "ghl_contact_id": "string" }
        ]
      }
    ]
  }
]
```

**Write rules:**
- Always update `_meta.last_updated`, `_meta.last_run`, `_meta.last_run_type`, and increment `_meta.total_runs` at the end of every run
- Merge new data into existing records — never replace a contact or deal record wholesale
- If a field is unknown, set it to `null` rather than omitting it
- Sender classifications, once written, are permanent unless overridden by a Suggestion

---

## The Training System

Joshua trains the skill entirely through the Suggestions section in the Notion daily page. No code changes required.

Write-in format (Joshua's freeform notes between runs):
```
💡 SUGGESTIONS
[freeform instruction, correction, new rule, new context]
```

Every suggestion is: applied this run → written to Living Context Store → written to master prompt if applicable → marked `✓ Added — [date]` → cleared next run.

The Suggestions section stays clean after every cycle. Knowledge is permanent. Joshua never teaches the same thing twice.

---

## Guardrails

**Never** read from any inbox other than `joshua@webberinvestmenthomes.com`.

**Never** query any GHL location other than `EKfRUZkioMTfy1vtYvua`.

**Never** overwrite or delete existing master prompt content — additive and dated only.

**Never** surface a Tier 3 email in the briefing.

**Never** create a duplicate task already on the Notion page — check before writing.

**Never** cache the Notion task page — always read live.

**Never** mark a Tier 1 or Tier 2 email as read without surfacing it in the briefing.

**Never** send a reply — only draft it. Joshua sends all replies himself.

If the inbox read fails, `living-context-store.json` cannot be read, or Notion is unreachable: halt, log the error, and notify Joshua rather than running with incomplete context. Never run without the Living Context Store — a missing or corrupted JSON file is a blocking error.

---

## Success Criteria

- Morning briefing is in Notion before 9:30 AM CT every weekday
- Afternoon briefing is in Notion before 5:00 PM CT every weekday
- All emails read are from `joshua@webberinvestmenthomes.com` only
- All GHL lookups happen inside `EKfRUZkioMTfy1vtYvua` only
- Both master prompts are read every run and updated when new context is learned
- Tier 1 emails have accurate, contextual task matches
- Reply drafts sound like Joshua wrote them (see `reply-style.md`)
- Tier 3 emails are never shown — handled invisibly
- Suggestions are absorbed, confirmed, and cleared within one run cycle
- Living Context Store grows more accurate with every run
- Joshua's email blocks shrink from 30 minutes to 5 minutes
