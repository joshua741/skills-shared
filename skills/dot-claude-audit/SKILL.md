---
name: dot-claude-audit
description: Use when auditing the ~/.claude folder to verify skills, docs, memory, and plugins are correctly placed. Catches misplaced reference docs, dead MEMORY.md links, skills missing SKILL.md, orphaned files in docs/, and memory files in the wrong project folder.
---

# .claude Folder Audit

Systematically check every meaningful location under `~/.claude/` and report what's wrong, what's fine, and what needs action. Write findings to a dated report file and send a notification summary.

## Audit Steps

### 1. Setup

```bash
REPORT_DIR="$HOME/.claude/audit-reports"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/$(date +%Y-%m-%d).md"
```

Start the report file with today's date as the header.

### 2. Skills Audit (`~/.claude/skills/`)

Check each item in the skills folder:

- **Each subdirectory must contain a `SKILL.md`** — flag any folder missing one
- **No loose `.md` files at the root of `skills/`** — they belong inside a named skill folder
- **Supporting files inside a skill folder should be referenced from that skill's `SKILL.md`** — read each SKILL.md and check that any sibling files are mentioned; flag unreferenced ones as potentially orphaned

### 3. Docs Audit (`~/.claude/docs/`)

- List every file in `docs/`
- For each file: determine if it is truly general reference (no owning skill) OR if it belongs inside a specific skill folder
- Flag any doc that is tightly coupled to a specific skill — it should live in that skill's folder as a supporting file
- If `docs/` is empty, note that — it's correct after proper organization

### 4. Memory Audit (all `~/.claude/projects/*/memory/` folders)

For each memory folder found:

**Index accuracy:**
- Read `MEMORY.md`
- For every link in the index, verify the target file exists — flag dead links
- For every `.md` file in the folder (except `MEMORY.md`), verify it appears in the index — flag unlisted files

**Project scope:**
- The folder name (e.g. `C--Users-joshu-wih-app`) encodes the working directory (`C:\Users\joshu\wih-app`)
- Flag if any memory file's content clearly belongs to a different project than the folder implies

### 5. Plugins Audit (`~/.claude/plugins/`)

- Read `installed_plugins.json` — list installed plugins and their versions
- Verify `plugins/cache/` contents match what's installed — flag any cache folder with no corresponding entry in `installed_plugins.json`
- Flag if any file inside `plugins/cache/` has been manually modified (check git status inside the cache folder if it's a git repo)
- Note: plugin cache is system-managed — manual edits break auto-updates

### 6. Settings Check

- Read `~/.claude/settings.json` — verify it is valid JSON
- Read `~/.claude/settings.local.json` if it exists — verify valid JSON
- Flag if `enabledPlugins` references a plugin not present in `installed_plugins.json`

## Report Format

Write findings to `$REPORT` using this structure:

```markdown
# .claude Folder Audit — YYYY-MM-DD

## Summary
X issues found. Y warnings. Z items clean.

## Issues (action required)
- [SKILLS] skill-name/ is missing SKILL.md
- [MEMORY] MEMORY.md links to wih-app-notes.md but file does not exist
- [DOCS] agent-teams-reference.md belongs under skills/agent-teams/ as a supporting file

## Warnings (review suggested)
- [SKILLS] email-brief/old-draft.md is not referenced in SKILL.md
- [PLUGINS] cache folder found for unknown-plugin with no installed_plugins.json entry

## Clean
- skills/build-app/ ✓
- skills/email-brief/ ✓
- skills/agent-teams/ ✓
- skills/skill-builder/ ✓
- projects/C--Users-joshu-wih-app/memory/ ✓ (index matches files)
- plugins/superpowers ✓

## Recommendations
[Specific next steps for each issue]
```

## Notification

After writing the report, send a push notification:

- **If issues found:** "⚠️ .claude audit: X issue(s) found — see ~/.claude/audit-reports/YYYY-MM-DD.md"
- **If clean:** "✓ .claude audit complete — everything looks good"

## Final Output

Tell the user:
1. The full path to the report file
2. A one-line summary of findings
3. Any issues that require immediate action
