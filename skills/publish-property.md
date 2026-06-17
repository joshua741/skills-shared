# Publish Property to Rent2OwnCribs Website

Publish a completed property listing to the Rent2OwnCribs Supabase database and set it as Available on the website.

---

## When to use this skill

Use this skill AFTER the following are already complete:
1. Property description has been generated (via `/rent-to-own-description`)
2. House photos have been watermarked (via `/rent-to-own-cribs-logo-adder`)
3. The user says the property is ready to go live (e.g. "make this available", "publish this", "add to the website")

---

## Step 1 — Read and order the watermarked photos

Read every image from the `WATERMARKED_COMPLETED_<PROPERTY>` folder in Downloads using the Read tool.

Identify what each photo shows, then sort them into this exact order:
1. Front of house (exterior / street view) — **always first**
2. Living room
3. Kitchen
4. Hallways
5. Secondary bedrooms
6. Secondary bathrooms
7. Master bedroom
8. Master bathroom
9. Backyard / outdoor space
10. Back of house

Not every property will have every category — skip any that don't exist. If a category has multiple photos, keep them together in sequence before moving to the next category.

After sorting, you will have an **ordered list of file paths**.

---

## Step 2 — Upload images to Supabase Storage

Run the upload script with the ordered file paths:

```
node "C:/Users/joshu/.claude/scripts/watermark/upload-images.js" "<property-slug>" "<path1>" "<path2>" ...
```

- `<property-slug>` = address in lowercase with spaces replaced by hyphens (e.g. `4513-48th-st`)
- File paths = the ordered list from Step 1, in order

The script outputs a JSON array of public URLs in the same order as the files passed in.

Parse the output — the **first URL** is `image_url`, the **rest** go into `additional_images`.

---

## Step 3 — Insert or update the property in Supabase

Use `mcp__claude_ai_Supabase__execute_sql` with project_id `catvxwoyguovitcyxwap`.

### Field mapping

| Field | Value |
|---|---|
| title | Street address only (e.g. "4513 48th St") |
| address | Full address (e.g. "4513 48th St, Lubbock, TX 79414") |
| location | City and state (e.g. "Lubbock, TX") |
| bedrooms | Integer |
| bathrooms | Integer |
| sqft | Integer |
| purchase_price | Calculated sales price (integer) |
| down_payment | Calculated RTO down payment (integer) |
| seller_finance_deposit | Calculated SF down payment (integer) |
| monthly_payment | Calculated PITI rounded to nearest $5 (integer) |
| status | 'Available' |
| condition | 'Move-In Ready' if move-in ready, otherwise 'As-Is' |
| neighborhood | Neighborhood name from research (if found) |
| hold_fee | Always **2000** |
| income_requirement | Always **monthly_payment × 3** (e.g. $2,525/mo → $7,575) |
| description | Body paragraphs only (see rule below) |
| image_url | First URL from upload script output |
| additional_images | Array of remaining URLs from upload script output |

### Description field rule

Store ONLY the body paragraphs — starting from "We're excited to offer..." through the final paragraph. Do NOT include:
- RENT TO OWN / SELLER FINANCE header lines
- 🏠 Price, 📍 Address, spec lines
- Monthly payment line
- "We do check credit" line
- Any phone number lines
- Any "Rent2OwnCribs Dot Com" lines
- "Our homes move quickly" closing line

### INSERT (new property)

```sql
INSERT INTO public.properties (
  title, address, location, bedrooms, bathrooms, sqft,
  purchase_price, down_payment, seller_finance_deposit, monthly_payment,
  hold_fee, income_requirement,
  status, condition, neighborhood, description,
  image_url, additional_images
) VALUES (
  '[title]', '[address]', '[location]', [beds], [baths], [sqft],
  [purchase_price], [rto_down], [sf_down], [monthly],
  2000, [monthly * 3],
  'Available', '[condition]', '[neighborhood]', '[body_description]',
  '[first_image_url]', ARRAY['[url2]','[url3]','[url4]']
) RETURNING id, title, status;
```

### UPDATE (property already exists)

```sql
UPDATE public.properties SET
  status = 'Available',
  description = '[body_description]',
  purchase_price = [purchase_price],
  down_payment = [rto_down],
  seller_finance_deposit = [sf_down],
  monthly_payment = [monthly],
  hold_fee = 2000,
  income_requirement = [monthly * 3],
  image_url = '[first_image_url]',
  additional_images = ARRAY['[url2]','[url3]','[url4]'],
  updated_at = now()
WHERE address = '[full_address]'
RETURNING id, title, status;
```

---

## Step 4 — Email Mostafa for Facebook Marketplace posting

After the Supabase insert/update succeeds, send an email to Mostafa using `mcp__claude_ai_Zapier__gmail_send_email` with the following:

**To:** mostafa.webberinvestmenthomes@gmail.com
**Subject:** New Property Ready for Facebook Marketplace – [Address]
**Body:** The FULL listing description — the complete version including the header block (RENT TO OWN / SELLER FINANCE lines), all pricing specs, phone numbers, and the call-to-action footer. This is the Facebook-ready copy, not the body-only version stored in the database.
**Attachments (`file` field):** Pass ALL of the Supabase public image URLs from Step 2 as the `file` array — in the same order (front of house first). The Zapier Gmail tool accepts public URLs directly as attachments, so no separate upload is needed since the images are already in Supabase Storage.

---

## Step 5 — Confirm

After both Supabase and the email are complete, confirm to the user:
> "✅ [Address] is now live on the website as Available. [N] photos uploaded in order. Email sent to Mostafa for Facebook Marketplace posting."
