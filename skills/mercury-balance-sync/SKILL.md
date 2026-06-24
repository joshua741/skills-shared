---
name: mercury-balance-sync
description: Use when checking Mercury bank/reserve balances for WIH properties, syncing balances to the Mortgage Status sheet, running or troubleshooting the MWF balance sync automation, or investigating low-balance alerts for Webber Investment Homes.
---

# Mercury Balance Sync — Webber Investment Homes

Syncs live Mercury account balances into the Mortgage Status sheet (columns AA/AB/AC) for all 13 active properties. Runs automatically MWF at 8 AM via scheduled task. Also triggers Telegram alerts and red cell highlighting when combined balances fall below the mortgage threshold.

## Credentials

- **Mercury API key:** `env.MERCURY_API_KEY` in `C:\Users\Mostafa Elkhamisy\.claude\settings.json`
  - Must include full `secret-token:` prefix in Bearer header
- **Telegram:** `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `C:\Users\Mostafa Elkhamisy\.claude\settings.local.json`

## Mercury API

```powershell
$token = (Get-Content "C:\Users\Mostafa Elkhamisy\.claude\settings.json" | ConvertFrom-Json).env.MERCURY_API_KEY
$headers = @{ Authorization = "Bearer $token" }
$accounts = (Invoke-RestMethod -Uri "https://api.mercury.com/api/v1/accounts" -Headers $headers).accounts
```

Account nicknames follow the pattern:
- `Bank - {street address}` → column AA (Bank Balance)
- `Reserve - {street address}` → column AB (Reserve Balance)

Match on street number/name only — ignore city/state suffix in sheet addresses.

## Sheet Details

- **Spreadsheet ID:** `18i5R-5EoQXjHg22lpn-7662ZuQQrLhB4sZmilqWyLdU`
- **Sheet:** `Mortgage Status` (sheetId: `1044053798`)
- **Active rows:** 2–14 (rows where column A is non-blank)

| Column | Header | Notes |
|--------|--------|-------|
| A | Address | Match key — ignore city/state |
| K | Mortgage Balance Due | Used for threshold |
| L | Normal Mortgage Payment | Used for threshold |
| AA | Bank Balance | Written by this automation |
| AB | Reserve Balance | Written by this automation |
| AC | Last Updated Balance Check | Written as M/D/YYYY |

## Writing Balances (per row)

```
PUT https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/Mortgage%20Status!AA{row}:AC{row}?valueInputOption=USER_ENTERED
Body: {"range": "Mortgage Status!AA{row}:AC{row}", "majorDimension": "ROWS", "values": [[bankBalance, reserveBalance, "M/D/YYYY"]]}
```

Use `google_sheets_make_api_mutating_request` Zapier MCP tool.

## Low Balance Alert

**Threshold:** `max(K, L)` per row  
**Condition:** `Bank Balance + Reserve Balance < threshold`

If any properties are flagged → send ONE Telegram message listing all flagged properties.

## Cell Color Highlighting

**Handled by a permanent conditional formatting rule in the sheet — do NOT write backgroundColor from code.**

- Rule formula: `=AND($A2<>"",$AA2+$AB2<MAX($K2,$L2))`
- Applied to: `AA2:AB14`
- Flagged = glossy red `{red: 0.91, green: 0.26, blue: 0.21}`
- Recovered = reverts to existing row formatting automatically

If the rule is ever deleted or broken, re-add it via:
```
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate
```
With an `addConditionalFormatRule` request targeting sheetId `1044053798`, columns 26–28 (AA:AB), rows 1–14.

## Scheduled Task

- **Task ID:** `mercury-balance-sync`
- **File:** `C:\Users\Mostafa Elkhamisy\.claude\scheduled-tasks\mercury-balance-sync\SKILL.md`
- **Schedule:** `0 8 * * 1,3,5` (Mon/Wed/Fri 8 AM local)
- **Notifications:** on
