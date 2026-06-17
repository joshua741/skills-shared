# skills-shared

Shared Claude Code skills for Webber Investment Homes / Webber Wealth Holdings.

This repo is the sync point between team members' `~/.claude/skills` folders.

## How it syncs

Each machine runs a scheduled task ("Claude Skills Sync") that, every 2 hours:

1. Commits any new/changed skills locally
2. Pulls everyone else's changes
3. Pushes its own

## Rules

- **Never commit live credentials.** Use placeholders (`YOUR_API_KEY`,
  `$DOORLOOP_API_KEY`) and keep real tokens in local, git-ignored files.
- Each skill lives in its own folder with a `SKILL.md`.
- Pre-existing per-user skills are intentionally git-ignored (see `.gitignore`);
  only skills added after setup are shared.
