# Baselane Bank Statement Query

Answer questions about transaction history, subscriptions, and property-specific expenses using the Bank Statements tab in the Property Payment Checklist spreadsheet.

---

## When to use this skill

Use when the user asks any of:
- "List all our subscriptions" / "What subscriptions do we have?"
- "What are highly likely subscriptions?"
- "How many times did we buy something for [property]?" or "What did we spend on [property]?"
- "What are our recurring charges?" / "What charges repeat every month?"
- "Show me all charges from [vendor name]"
- "How much did we spend on [category] this month/year?"
- "What transactions came in from [month/year]?"
- Anything about bank statement data, transaction history, or expense analysis

---

## Step 1 — Read all bank statement data

Use `mcp__claude_ai_Zapier__google_sheets_get_data_range` with:
- **Spreadsheet:** `18i5R-5EoQXjHg22lpn-7662ZuQQrLhB4sZmilqWyLdU`
- **Worksheet:** `Bank Statements`
- **Range:** `A:L` (all columns)

**Column layout:**

| Col | Name | Description |
|-----|------|-------------|
| A | Date | Transaction date (MM/DD/YYYY) |
| B | Vendor / Description | Raw description from bank statement |
| C | Amount | Dollar amount (negative = expense, positive = income/credit) |
| D | Type | Debit or Credit |
| E | Property | Property address (e.g., "4019 37th St") |
| F | Account Name | Baselane account name |
| G | Category | Utilities / Subscription / Maintenance / Supplies / Insurance / Management Fee / Transfer / Income / Other |
| H | Statement Month | Format: YYYY-MM (e.g., 2026-05) |
| I | Is Subscription | Yes / No |
| J | Subscription Name | Cleaned vendor name if subscription |
| K | Notes | Manual notes |
| L | Date Imported | When this row was imported by automation |

If the sheet is empty, tell the user: "No bank statement data has been imported yet. The N8N automation imports statements on the 1st of each month — or you can trigger it manually."

---

## Step 2 — Answer the query

### "List subscriptions" / "What subscriptions do we have?"
1. Filter rows where Column I = "Yes"
2. Also detect additional subscriptions by finding same vendor + same/similar amount (within $2) appearing in 2+ different Statement Months — **exclude utilities** (see list below)
3. Group by vendor: Vendor | Monthly Amount | Properties Charged | First Seen | Times Charged
4. Sort by amount descending

### "Highly likely subscriptions"
Same as above, but also flag vendors appearing 2+ times with amounts within $5 of each other. Mark confidence:
- **High** — 3+ months, consistent amount
- **Medium** — 2 months, or amount varies slightly
- Also flag vendors containing: INC, LLC, .COM, SOFTWARE, SUBSCRIPTION, MONTHLY, ANNUAL, PRO, PREMIUM, SAAS, SERVICES, CLOUD, TECH, DIGITAL

### "What did we spend on [property]?" / "Purchases for [property]?"
1. Filter Column E matching the property (partial match OK — "37th" matches "4019 37th St")
2. **Exclude** rows where Column G = "Utilities"
3. Group by vendor: Vendor | Count | Total Amount | Most Recent Date | Category
4. Summary line: "X unique vendors, Y transactions, $Z total (utilities excluded)"

### "Show charges from [vendor]"
Filter Column B (case-insensitive) for the vendor name. Show: Date | Vendor | Amount | Property | Category | Statement Month. Include count and total at bottom.

### "Spending by category"
Filter Column G for the category. Group by Property with subtotals and a grand total.

### "Transactions from [month/year]"
Filter Column H for the YYYY-MM. Group by Property, show income vs. expenses separately.

---

## Utilities to exclude from subscription analysis

Never flag these as subscriptions:
- **Electric:** Lubbock Power & Light, AEP Texas, Xcel, Oncor, Reliant, TXU, SPS, City of Lubbock Electric
- **Water/Sewer:** City of Lubbock Water, Municipal Water, Water Dept
- **Gas:** Atmos Energy, CenterPoint Energy
- **Internet/Cable:** AT&T, Xfinity, Comcast, Spectrum, Suddenlink, Cox, Windstream
- **Trash:** WCA Waste, Republic Services, Waste Management, City of Lubbock Solid Waste
- Generic keywords in vendor name: CITY OF, UTILITY, UTILITIES, MUNICIPAL, ELECTRIC, GAS BILL, WATER BILL

---

## Property → Account mapping

- **4019 37th St Lubbock** → W&M Series LLC - 4019 37TH STREET SERIES
- **3423 E Baylor St Lubbock** → W&M Series LLC - 3423 E Baylor Street Series
- **2102 68th St Lubbock** → W&M Series LLC - 2102 66th Street Series
- **1926 27th St Lubbock** → W&M Series LLC - 1926 27th Street Series
- **All others** → Webber Wealth Holdings LLC

---

## Step 3 — Format the response

Open every response with:
- Date range: "Showing data from [earliest month] to [latest month]"
- Scope: "X total transactions across Y statements"

Use markdown tables for results. Format all dollar amounts as `$X,XXX.XX`. Group by property when multiple properties are involved. End with a one-line insight if something stands out.
