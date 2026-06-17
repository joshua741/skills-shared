# Baselane Statement Download

Manually trigger the Baselane monthly statement download, check its status, or troubleshoot it.

---

## When to use this skill

Use when the user says any of:
- "Run the Baselane download"
- "Download my bank statements"
- "Trigger the statement import"
- "Check if the Baselane automation ran"
- "The Baselane download failed" / "Why didn't it run?"
- "Manually run the monthly automation"

---

## N8N Configuration (always reference this)

- **N8N URL:** http://localhost:5678
- **API Key:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMTZhZjI5Yy0xZjE5LTRkMjMtOGJhZC01ZDI1NTNjZmJjNTUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiY2M1ZjVkOTAtNDBhMS00ZDQ4LTg3ZmYtZWY1NWMxM2ViMTM3IiwiaWF0IjoxNzgwMzk5MzAwLCJleHAiOjE3ODI5NjQ4MDB9.WC8yjGUmTO4HmNUYgUJ8aQQDXGUTWEEf0RAtipljWE4
- **Main Workflow ID:** SI4uoCtAD4UTHb2k (Baselane Monthly Statement Downloader)
- **MFA Receiver ID:** IWc9VJHNXPzpzjqq (Baselane MFA Receiver - Always On)
- **Twilio notification number:** (806) 602-9276
- **Joshua's phone:** +18067818495
- **Spreadsheet ID:** 18i5R-5EoQXjHg22lpn-7662ZuQQrLhB4sZmilqWyLdU

---

## Step 1 — Check N8N is running

Run this PowerShell command to verify N8N is up:
```
netstat -ano | findstr ":5678" | findstr "LISTENING"
```

If nothing returns, N8N is down. Start it:
```
Start-Process "cmd.exe" -ArgumentList "/c $env:APPDATA\npm\n8n.cmd start" -WindowStyle Minimized
```

Also check the Cloudflare tunnel is running:
```
Get-Process | Where-Object { $_.ProcessName -like "*cloudflared*" }
```

If tunnel is down, restart it:
```
Start-Process -FilePath "$env:USERPROFILE\cloudflared.exe" -ArgumentList "tunnel --url http://localhost:5678" -RedirectStandardError "$env:USERPROFILE\cloudflared-err.log" -WindowStyle Hidden
Start-Sleep -Seconds 6
Get-Content "$env:USERPROFILE\cloudflared-err.log" | Select-String "trycloudflare.com"
```
Get the new URL and update Twilio's webhook for (806) 602-9276.

---

## Step 2 — Trigger a manual run

Use PowerShell to call the N8N execute endpoint:

```powershell
$apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMTZhZjI5Yy0xZjE5LTRkMjMtOGJhZC01ZDI1NTNjZmJjNTUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiY2M1ZjVkOTAtNDBhMS00ZDQ4LTg3ZmYtZWY1NWMxM2ViMTM3IiwiaWF0IjoxNzgwMzk5MzAwLCJleHAiOjE3ODI5NjQ4MDB9.WC8yjGUmTO4HmNUYgUJ8aQQDXGUTWEEf0RAtipljWE4"
$h = @{ "X-N8N-API-KEY" = $apiKey; "Content-Type" = "application/json" }
Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows/SI4uoCtAD4UTHb2k/run" -Method POST -Headers $h -Body '{}'
```

If "POST method not allowed", use the N8N UI instead:
1. Go to `http://localhost:5678`
2. Open "Baselane Monthly Statement Downloader"
3. Click "Test workflow" button

---

## Step 3 — Monitor the run

Check recent execution status:
```powershell
$apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
$h = @{ "X-N8N-API-KEY" = $apiKey }
$e = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/executions?limit=3" -Headers $h
$e.data | Format-Table id, status, startedAt
```

---

## Step 4 — When MFA is requested

When Baselane needs verification:
1. You'll get a text from **(806) 602-9276**: "Baselane automation is running. Reply with your 6-digit verification code now."
2. Reply to that text with the 6-digit code from Baselane
3. The automation reads it from Google Sheets and continues automatically

---

## Step 5 — Verify results

After completion, check the Bank Statements tab:
- Open Property Payment Checklist → Bank Statements tab
- Or ask Claude: "What are our subscriptions?" to query the imported data

---

## Monthly schedule

The automation runs automatically on the **1st of every month at 9:00 AM** as long as:
- Your computer is on and logged in
- N8N is running (it auto-starts on Windows login)
- The Cloudflare tunnel is active

**Note:** If your computer is off on the 1st, the trigger will be missed. Railway deployment will fix this permanently.

---

## Troubleshooting

**"Cloudflare URL changed"** — update Twilio webhook for (806) 602-9276 with the new URL from cloudflared-err.log

**"No statements found"** — Baselane may have updated their UI. The Puppeteer selectors in the workflow may need updating.

**"Google Sheets credential expired"** — go to N8N → Credentials → Google Sheets account → reconnect
