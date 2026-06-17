# Email Reply Skill

Trigger phrase: "email reply"

---

## Prerequisites

This skill requires Gmail connected to Claude Code via MCP.
Without it, this skill will not work.

If you have not set this up yet, stop here and complete that first.

---

## First-Time Setup

When this skill runs, check if the Setup section below still contains
placeholder values (YOUR_EMAIL or YOUR_NAME). If it does, run the
setup flow before anything else.

### Setup Flow

1. Ask: "What is your email address?"
2. Ask: "What is your first name?"
3. Tell the user: "Give me a moment -- I'm going to pull your recent
   sent emails and build a tone profile from your actual writing."
4. Search Gmail for the last 15 sent emails from the user
5. Analyze them and extract a personalized tone profile covering:
   - Greeting style
   - Opening line patterns
   - Body writing style
   - How they decline or say no
   - Sign-off
   - Formatting habits
6. Edit this SKILL.md file and replace the Setup and Tone Profile
   sections with the user's real values
7. Confirm: "Setup complete. Your skill is now personalized to your
   writing style. Running your first email check now..."
8. Continue immediately to Step 1 below

---

## Setup

- **Email:** YOUR_EMAIL
- **Name:** YOUR_NAME

---

## Step 1: Pull Emails

Search Gmail for emails that need a response from the last 14 days.

- Exclude: promotions, newsletters, notifications, automated emails,
  receipts, shipping updates
- Include: direct outreach, partnership inquiries, business emails,
  personal messages
- Sort by oldest first
- Show 10 at a time
- If more than 10 emails are found, tell the user: "I found X emails
  but I'm showing you the 10 oldest first. Run 'email reply' again
  when you're done to see the rest."

---

## Step 2: Display the Summary

Show this exact format. Do not add anything extra.

---

X emails need your response. Type a brief response next to each one
-- "yes", "no", "not interested", "I'm busy until [date]", anything
short. Then say "done" when ready.

---

1.
SUBJECT: [subject line]
FROM: [sender name] -- [email address]
SUMMARY: [2-3 sentences max -- what they want and why it matters]
YOUR RESPONSE:

---

(continue for each email)

---

## Step 3: Open Response File

Write the email list to a temporary file and open it in the user's
editor so they can type their responses directly without copy-pasting
into the chat. Tell the user: "Fill in your responses, save the file,
then come back and say done."

---

## Step 4: Wait

Do not proceed until the user says "done" or "draft the emails".

---

## Step 5: Draft the Replies

Read the response file. For each email where the user typed a
response, write a full reply using the Tone Profile below.

Use gmail_create_draft to save each reply as a draft. DO NOT send
anything.

When all drafts are created, confirm with a simple list:

Drafts created:
- [Sender name] -- [subject]
- [Sender name] -- [subject]

Done. Review them in your Gmail drafts and send when ready.

---

## Tone Profile

(This section is automatically generated during first-time setup
and replaced with your personal writing style.)

**Greeting:** Always "Hi [First Name]," -- never "Dear", never "Hey"

**Opening line:**
- Use "Thank you for..." only when genuinely warranted
- Skip it if it feels forced -- get straight to the point

**Body:**
- 2-4 short sentences max per paragraph
- One idea per sentence
- Direct -- say exactly what you mean
- No filler: no "I hope this finds you well", no "just wanted to
  circle back"
- One clear question at a time when asking for something

**Declining:**
- Polite but clear: "I'm not focusing on X at the moment, so now
  is not the right time for me"
- No over-explaining or apologizing

**Sign-off:**
Best,
[Your Name]

**Format:**
- No bullet points in emails
- No emojis
