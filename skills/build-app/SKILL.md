---
name: build-app
description: Use when building a new full-stack application from scratch — especially apps with SMS/voice (Twilio), AI conversations (Claude API), real-time dashboards (WebSocket), PostgreSQL, and Railway deployment.
---

# Build App

## Overview

Systematic process for going from idea to deployed full-stack app. Covers stack selection, project structure, backend/frontend build, third-party integrations, and Railway deployment — with lessons from real builds that prevent hours of debugging.

## Stack (Proven)

| Layer | Choice | Why |
|---|---|---|
| Runtime | Node.js 20+ | Required for Vite 6, modern packages |
| Backend | Express 5 + TypeScript | Typed, fast, Railway-native |
| Database | PostgreSQL (Railway or Supabase) | Reliable, free tier, SQL |
| Frontend | React + Vite + Tailwind | Fast build, great DX |
| Realtime | WebSocket (`ws` package) | Simple, no extra infra |
| SMS/Voice | Twilio (API Key auth) | More stable than Auth Token |
| AI | Claude API (`@anthropic-ai/sdk`) | claude-sonnet-4-6 for production |
| Deploy | Railway (Nixpacks) | One push, auto-deploy |

## Project Structure

```
app/
  src/
    server.ts           # Express entry point
    db/
      pool.ts           # pg Pool singleton
      schema.sql        # All tables + seeds
      migrate.ts        # Runs schema.sql on startup
    routes/
      api.ts            # REST endpoints
      sms.ts            # Twilio SMS webhooks
      voice.ts          # Twilio Voice webhooks
    services/
      ai.ts             # Claude conversation engine
      compliance.ts     # DNC, opt-out, human takeover
      dealRouting.ts    # Business logic
    websocket/
      server.ts         # WebSocket broadcast
  client/               # React frontend (separate npm workspace)
    src/
      api.ts            # All fetch calls
      types.ts          # Shared TypeScript types
      context/          # React context (state)
      components/       # UI components
      hooks/            # WebSocket hook
  .env                  # Local secrets (gitignored)
  railway.toml          # Deploy config
  package.json
```

## Critical Files

### railway.toml
```toml
[build]
builder = "NIXPACKS"
buildCommand = "npm install --include=dev && npm run build && cd client && npm install --include=dev && npm run build && cd .."

[deploy]
startCommand = "npm run migrate && node dist/server.js"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[nixpacks]
providers = ["node"]
```

**Why `--include=dev`:** Railway sets `NODE_ENV=production`, which makes npm skip devDependencies. TypeScript (`tsc`) lives in devDependencies — without this flag the build fails with exit 127.

**Why `providers = ["node"]:** Without this, Nixpacks may detect the React frontend and deploy with Caddy (static server) instead of Node. Breaks everything.

### .nvmrc
```
20
```

### package.json engines
```json
"engines": { "node": ">=20.0.0" }
```

### server.ts — Express 5 wildcard (CRITICAL)
```typescript
// Express 5 uses path-to-regexp v8 — bare * is INVALID
// ❌ WRONG: app.get('*', handler)
// ✅ CORRECT:
app.get('/{*splat}', (_req, res) => {
  res.sendFile(path.join(clientDist, 'index.html'))
})
```

## Twilio Integration

**Always use API Key auth — not Auth Token:**
```typescript
const client = twilio(
  process.env.TWILIO_API_KEY!,
  process.env.TWILIO_API_SECRET!,
  { accountSid: process.env.TWILIO_ACCOUNT_SID! }
)
```

Auth Tokens can become invalid or rotated. API Keys are more stable and can be scoped.

**Webhook URL format:** `https://your-app.up.railway.app/webhooks/sms`
Set this in Twilio Console → Phone Numbers → Messaging Configuration.

**Inbound SMS middleware order matters:**
```typescript
app.use('/webhooks', express.urlencoded({ extended: false })) // Must come before json()
app.use(express.json())
```

## Railway Environment Variables

These must be set manually in Railway → Service → Variables (`.env` is gitignored):

```
TWILIO_ACCOUNT_SID
TWILIO_API_KEY
TWILIO_API_SECRET
TWILIO_OUTREACH_NUMBER
TWILIO_SELLER_NUMBER
ANTHROPIC_API_KEY
DATABASE_URL         (set to ${{Postgres.DATABASE_URL}} reference)
WEBHOOK_BASE_URL     (https://your-app.up.railway.app — no trailing slash)
NODE_ENV             production
JOSH_PHONE
ANGEL_PHONE
```

## Database Pattern

```typescript
// pool.ts — one pool, reused everywhere
import { Pool } from 'pg'
export const pool = new Pool({ connectionString: process.env.DATABASE_URL })

// migrate.ts — idempotent schema
import { pool } from './pool'
import fs from 'fs'
import path from 'path'

async function migrate() {
  const sql = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8')
  await pool.query(sql)
  console.log('[MIGRATE] Done.')
}
migrate().then(() => process.exit(0)).catch(err => { console.error(err); process.exit(1) })
```

Use `CREATE TABLE IF NOT EXISTS` and `ON CONFLICT DO NOTHING` everywhere so migrations are safe to re-run.

## WebSocket Broadcast

```typescript
// server.ts — one pattern
import { broadcast } from './websocket/server'
broadcast('event:name', { ...payload })

// Client — useWebSocket hook
ws.onmessage = (e) => {
  const { event, payload } = JSON.parse(e.data)
  // dispatch to React context
}
```

## Common Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Build fails `tsc not found` | devDeps skipped in prod | Add `--include=dev` to build command |
| Railway deploys Caddy instead of Node | Nixpacks detects React first | Add `providers = ["node"]` in railway.toml |
| Server crashes on start `PathError *` | Express 5 wildcard syntax | Use `/{*splat}` not `*` |
| Twilio webhook not firing | URL not saved / wrong path | Confirm URL ends in `/webhooks/sms`, method POST |
| SMS not sending (401) | Wrong auth token | Switch to API Key auth |
| AI not responding to texts | `ai_active` default or env vars missing | Confirm Railway env vars are all set |
| Migration fails ECONNREFUSED | No Postgres service in Railway project | Add Postgres to same Railway project |

## Build Order

1. **Schema first** — design all tables before writing routes
2. **Migration + health check** — verify DB connects before building features
3. **Webhooks** — get inbound data flowing before AI
4. **AI service** — build conversation logic against real inbound data
5. **API routes** — build REST after core flow works
6. **Frontend** — build UI last, against working API
7. **Deploy** — push to Railway, set env vars, test end-to-end
8. **Twilio webhooks** — point Twilio at Railway URL after deploy succeeds

## Testing Checklist

- [ ] `GET /health` returns `{"status":"ok"}`
- [ ] Text inbound number → Railway logs show `[SMS] Inbound`
- [ ] AI replies within 5 seconds
- [ ] Dashboard loads and shows the lead
- [ ] WebSocket updates in real time (no refresh needed)
- [ ] Manual reply from dashboard sends via Twilio
- [ ] Stage move updates the card immediately
