# Triage Rules — Email Brief Skill

## The Three Filters

Every unread email from `joshua@webberinvestmenthomes.com` is scored against three filters:

**Contact filter** — Is the sender in the Living Context Store as a known deal contact, team member, financial platform, or active relationship? Classification is built dynamically from GHL (`EKfRUZkioMTfy1vtYvua`), Notion, and prior correspondence. Unknown senders get classified on first encounter.

**Deal filter** — Does the email contain any of: a property address, dollar amount, deadline, closing date, escrow reference, title reference, or the name of an active deal, entity, or pipeline stage?

**Action filter** — Does the email contain any of: a question, a request, a document, a quote, a payment confirmation, a payment failure, or any implied next step?

---

## Triage Tiers

**Tier 1 — Always surface**
- Matches two or three filters, OR
- Comes from a financial platform with account activity (fund distributions, financial alerts, mail notifications)

Always appears in the briefing. Always reviewed.

**Tier 2 — Surface, review when time allows**
- Matches one filter, OR
- Comes from a service provider with a potentially relevant update (utility companies when payment-related, mortgage servicers with account activity, financial platforms with non-promotional content)

Appears in the secondary list of the briefing.

**Tier 3 — Auto-handle invisibly**
- Matches no filters, OR
- Classified as promotional, OR
- General notification with no action required

Mark read automatically. Log sender and subject to Living Context Store. Never show in briefing unless Joshua explicitly asks via Suggestions.

---

## Sender Classification Registry

Classification is built dynamically. The first time a sender appears, classify them based on content and context. Store that classification permanently. These are example patterns — not a hardcoded starting list:

| Sender Type | Default Tier |
|---|---|
| Financial fund tracking platforms (account activity) | Tier 1 |
| Financial fund tracking platforms (promotional) | Tier 3 |
| Property banking platforms (financial alerts) | Tier 1 |
| Property banking platforms (promotional) | Tier 3 |
| Virtual address / mail services (mail notification) | Tier 2 |
| Utility providers (payment alert) | Tier 2 |
| Utility providers (general update) | Tier 3 |
| Mortgage servicers (account activity) | Tier 2 |
| Mortgage servicers (general notification) | Tier 3 |
| Promotional / marketing senders | Tier 3, never surface |
| Deal contacts (known from GHL/Notion) | Score against all 3 filters |
| Team members (internal) | Score against all 3 filters |
| Title companies, attorneys, lenders | Score against all 3 filters |
| Unknown first-time senders | Classify on first encounter via content + GHL lookup |

---

## Classification Behavior

When an unrecognized sender appears:
1. Check GHL (`EKfRUZkioMTfy1vtYvua`) by email address first, then by name
2. If found in GHL: read their pipeline stage, tags, and internal notes. Use this to classify and score.
3. If not found in GHL: classify based on email content, subject line, and domain patterns
4. Store classification in the Sender Classification Registry permanently
5. Apply it to this email and all future emails from this sender

A classification stored in the registry is never re-evaluated from scratch. If Joshua wants to change a classification, he does so via the Suggestions section.

---

## Scoring Notes

- One email can hit all three filters — still Tier 1, just a strong match
- A known contact with a non-deal, non-action email can still be Tier 2 or Tier 3 based on content
- Needle Mover match always promotes to top of briefing regardless of tier
- When in doubt between Tier 1 and Tier 2, lean Tier 1 — Joshua's time is better spent reviewing one extra email than missing something important
- When in doubt between Tier 2 and Tier 3 for promotional content, always Tier 3 — do not surface noise
