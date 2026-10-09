# Yelp · Find & Win: Demo Flow and Script

**Segment:** Find → Win on the Agentic Revenue Lifecycle
**Run time:** 23–26 minutes
**Audience:** Nina (CRO), Dana (VP RevOps), Marcus (Sr Dir, Emerging & Multi-Location), Priya (Dir, Demand Gen)
**Story in one line:** Piper finds the invisible owner in one conversation. Hunter uses that record as the template to find all of them. Salesforce keeps the record, and Flow routes it.

---

## Limitations to call out (say these out loud)

| Item | What's real | What to say |
|---|---|---|
| **Piper** | Mockup (`prototypes/piper.html`). Piper can't be installed in this demo org. The real Piper runs in the EDO if you want a live voice moment. | "What you're seeing is a recreation of Piper on a Yelp for Business page. The CRM write-back and routing you'll see next are real, running in Salesforce." |
| **Hunter** | Mockup (`prototypes/hunter.html`) modeled on the Hunter prototype. Hunter isn't generally available. | "Hunter is early. This is a prototype; the experience and naming will change. The only call to action today is the beta waitlist." **Don't quote a date or promise beta acceptance.** |
| **Salesforce** | **Real.** Custom fields, the record-triggered Flow, the Lead, Task, Event, the 40-operator hierarchy (402 accounts), contacts, campaign, 10 opportunities, and 40 brief tasks. | "Everything from here on is live in the org." |
| **Numbers** | The territory totals (400 / 1,700 / 1,100 / 600 / $1.62M) come from the demo narrative. The top 40 operators in the org are generated data. The $2,700 revenue per location is Yelp's derived public figure. | Treat as illustrative. |

---

## Before the demo

1. Reset the data (about 1 minute). This also re-fires the routing Flow on the Piper lead:
   ```bash
   python3 scripts/seed.py
   ```
   If you only want to re-fire the Piper lead (for example, right before the call), run `python3 scripts/seed.py --piper`.
2. Serve the mockups:
   ```bash
   python3 -m http.server 8787 --directory prototypes
   ```
3. Open full-screen tabs **in this order**, then swipe between them:
   1. `http://localhost:8787/piper.html`
   2. Salesforce → **Leads → "Piper - Multi-Location Leads"**, then open **Sam Whitaker**
   3. Salesforce → **Setup → Flows → Yelp - Multi-Location Lead Routing** (canvas view)
   4. `http://localhost:8787/hunter.html`
   5. Salesforce → **Accounts → "Hunter - Colorado Operators (Ranked)"**
   6. Salesforce → **Pikes Peak Food Co.** (rank #1) → **View Account Hierarchy**
4. In the mockups: **→ / Space / clicker** = next, **←** = back, **R** = restart, **H** = hide the presenter strip at the top. To rehearse a single beat, add `?step=N` to the URL (for example `piper.html?step=11`).
5. Sign in as Rob: `sf org open -o trailsignup-429cdf`
6. **Hide the real URL.** Open each mockup in Chrome app mode, which has no address bar or tabs:
   ```bash
   open -na "Google Chrome" --args --app="https://rhauser15.github.io/PeerCert/piper.html?frame=1"
   ```
   ```bash
   open -na "Google Chrome" --args --app="https://rhauser15.github.io/PeerCert/hunter.html?frame=1"
   ```
   `?frame=1` (or pressing **B**) adds a fake Chrome tab and address bar. Piper shows `biz.yelp.com/advertise/checkout…`, then `…/multi-location` when Piper co-browses. Hunter shows `yelp.lightning.force.com/lightning/n/Hunter`. Press **⌃⌘F** for full screen. Your B choice is remembered.

---

## 0 · Open: frame the problem (2 min)

**Say:**
> Nina, you've told the board AI changes the paying-locations trajectory. Today I want to show you where the first locations come from, without a single new hire.
>
> Dana's hypothesis from our last call is that Yelp is missing qualified multi-location owners because the signals are siloed. Priya's chat tool books meetings during business hours. Marcus's reps research a franchise group by hand for a day. And the data that would connect these owners lives in **billing**, not in the sales data model.
>
> On our lifecycle map, this is **Find and Win**: Piper on your inbound, Hunter on prospecting and the long tail, and Flow keeping the top of the funnel accurate. The PRIME levers it moves are **Pipeline Velocity, CAC Reduction, and Automate Outreach**.

**Show:** the lifecycle slide, with Find → Win highlighted.

---

## 1 · Piper: the invisible owner (7 min)

**Tab:** `piper.html` · **Steps 0–16** · Click path adapted from the *Qualified 10-Click Piper Demo [EDO]* guide (pinned mode, buyer profile, voice, co-browse, meeting booker, omnichannel follow-up), retold for Yelp.

| Step | Do | Say |
|---|---|---|
| 0 | Page loads | "Tuesday, 10:15 PM. Priya's chat tool has been off for four hours. A man is signing up to advertise one Smoothie King in Lakewood at $300 a month. Notice Piper isn't a chat bubble in the corner. She's **pinned** to the Yelp for Business site as an always-on ride-along, and she's already greeted him in context: his claimed page, his plan." |
| 1 | → (Yelp's signals card) | "Here's what Yelp's own data says: one location, 60 reviews, opened 2024. Long tail, self-serve, no rep. **The system is right on the data and wrong on the opportunity.**" |
| 2 | → (Piper's buyer profile) | "Meanwhile Piper is building a buyer profile from Salesforce and his web activity. He's looked at the multi-location page twice this week. That doesn't match a one-store buyer." |
| 3 | → | "So Piper nudges him based on what he's actually doing." |
| 4 | → (Speak with Piper) | "He switches to voice. Local owners research at night, from the car, between shifts. Piper meets them in whatever mode they want." |
| 5 | → (highlighted question) | "Piper asks the question no form asks: **'Is this your only location, or do you operate others?'**" *(pause)* |
| 6 | → | "Seven Dave's Hot Chicken, four Jersey Mike's, Denver metro and Colorado Springs, plus this Smoothie King." |
| 7–8 | → → | "Piper qualifies who controls the budget: him, for all of them." |
| 9–10 | → → | "And growth: development rights for four more through 2028." |
| 11 | → (co-browse) | "Now Piper **co-browses**. She knows every corner of the site, so she takes him to the multi-location page and pulls up the story that fits a multi-brand franchisee. He doesn't have to hunt for it." |
| 12 | → (reveal) | "Here's why Yelp could never find him. Twelve pages that share no name, so brand matching returns nothing. Each is claimed by a store manager under a store email. **His name is on none of them.**" |
| 13 | → (meeting booker) | "Piper doesn't upsell him a bigger self-serve plan. She turns on tonight's ad so he's live this weekend, then opens the booker with the **right** rep, Cindy on Marcus's team, using Salesforce routing." |
| 14 | → (Thu 10:00 + note) | "He books Thursday at 10:00 and asks Piper to tell the team what he wants. Piper relays it to the rep. At 10:15 on a Tuesday night, with no SDR involved." |
| 15 | → (recap email) | "Then the follow-up is instant, and it happens in the other channel that matters for inbound: the inbox. The recap isn't generic; it's this conversation. If he replies, Piper keeps going over email." |
| 16 | → (write-back panel) | "$3,600 a year as signed. About $32,000 across twelve locations at Yelp's own average, and $43,000 at sixteen by 2028. Piper writes `operates_other_brands = true`, `location_count = 12`, tags it multi-location, and books the rep. Let's prove that's real." |

**Lever callout (Priya):** speed to lead goes from 4 hours to zero, after hours, and the 60% of inbound no human works gets worked. Piper also runs alongside the incumbent chat tool, so the March renewal isn't a blocker for a pilot.

**Optional live beat:** Piper's voice, video, and multilingual features run live in the EDO (`edo.my.site.com/personalization`). If you want to show her speaking, cut there for 60 seconds after step 4 (*"Parlez-vous français?"* works well; for Yelp, try Spanish for a store manager). Then come back to the Yelp mockup for the story. Share your screen **with sound**.

---

## 2 · Proof, part 1: written back to Salesforce (4 min)

**Tab:** Salesforce Lead **Sam Whitaker**

| Do | Say |
|---|---|
| Show the **Yelp Agent Signals** section: Agent Source = Piper, Location Count 12, Brand Count 3, Brands Operated, Committed Future Locations 4 (through 2028), Self-Serve Monthly Spend $300, Unrealized Annual Spend $29,700 | "Dana, this is the conversation as structured CRM fields. No rep typed anything." |
| Show **Agent Qualification Summary** | "Here's what Piper learned, in plain language, on the record." |
| Point at **Owner = Cindy Central**, Status Qualified, Rating Hot, **Routing Reason** | "And it's already routed." |
| Activity: **Task "Agent brief…"** due tomorrow and **Event "Intro… (booked by Piper)"** Thursday 10:00 | "Cindy walks into Thursday knowing everything. Sam doesn't repeat himself." |
| Switch to the **Flow** tab | "This is the GTM Engineering box on the map. A record-triggered Flow: 3+ locations or other brands → flag multi-location, route to Marcus's team, create the brief. It runs on-platform, inside your API limits, and it's debuggable. That's the opposite of the enrichment workflow that ate your API limit before quarter close." |
| Optional: Leads list view **"Piper - Multi-Location Leads"** | "Every agent-qualified multi-location lead lands in one place." |

**Transition:**
> One owner. That proves the pattern exists. Marcus's question is how many more Sams there are. That's Hunter's job.

---

## 3 · Hunter: find all of them (7 min)

**Tab:** `hunter.html` · **Steps 0–6**

| Step | Do | Say |
|---|---|---|
| 0 | Page loads | "Marcus logs in. Hunter is already showing him the pattern Piper confirmed overnight." |
| 1 | → (objective types in) | "Here's the pivot. Yelp already owns every business page in America, so Hunter's objective isn't 'find businesses.' It's this: **identify Colorado operators controlling three or more paying locations across different brand names, and rank them by unrealized spend.**" |
| 2 | → (plan) | "Hunter uses Sam's record as the template. The signal that matters is one Yelp already owns and doesn't use for prospecting, because it lives in **billing**: the same payment method, billing address or billing contact across single-location self-serve accounts in different brands. Plus phone routing, the same person answering reviews, co-located openings, and entity and registered-agent data through the **Data Vendor Gateway**." Point at the guardrails: "Long-horizon runtime, inside platform limits, and every lookup logged through the Einstein Trust Layer. Dana, that's your audit trail, not reps pasting advertiser data into consumer AI tools." |
| 3 | → (Approve & start) | "This isn't a chat answer. It runs for days, which is what the long-horizon runtime is for." |
| 4 | → (3 days later) | "Colorado pilot territory: **about 400 operators controlling 1,700 locations.** Around **1,100 are already paying, at self-serve rates**, as unrelated accounts. The other **600 aren't advertising at all.** At Yelp's average revenue per location, that's **$1.6M of net-new annual revenue in one state**, inside the existing customer base, from accounts Yelp has billed for years without knowing they were connected." Point at the orange bars: "The strongest signals came from billing." |
| 5 | → (operator #1 drawer) | "Pikes Peak Food Co.: 18 locations, 2 brands, 10 dark. Here's the evidence, the hierarchy Hunter built, and the brief the rep gets." |
| 6 | → (worked it) | "Then Hunter works it: outbound sequences against the 600 dark locations, a parent-child hierarchy for each operator, and the top 40 by value routed to Marcus's reps with a brief. **Marcus's 180 reps stop staring at 10,000 undifferentiated business pages and start working a ranked list of named owners.**" |

**Lever callout (Marcus):** a day of manual research per franchise group becomes a brief that's waiting for the rep, and his top reps' private AI workflows become a governed team-wide motion.

---

## 4 · Proof, part 2: the rep's view in Salesforce (4 min)

| Do | Say |
|---|---|
| **Accounts → "Hunter - Colorado Operators (Ranked)"**: sort by Hunter Rank | "The top 40 operators, ranked: locations, paying, dark, unrealized spend, confidence, owner." |
| Open **Pikes Peak Food Co.** → **Yelp Agent Signals** + **Hunter Signals** | "The evidence is on the record, so the rep can see why." |
| **View Account Hierarchy** | "Eighteen location accounts under one owner. Before Hunter, these were eighteen strangers." |
| Activity: **"Hunter brief: …"** task | "The brief: who the principal is, what they pay today, what's dark, and a suggested opener." |
| Related: **Opportunity "Multi-Location Activation"** | "Pipeline Marcus can forecast. Hunter opened ten of them." |
| **Accounts → "Hunter - Dark Locations (In Sequence)"** | "The dark locations Hunter is sequencing." |
| Optional: **Campaign "Hunter - Colorado Dark Location Outreach"** | "And the outreach is attributable." |

**Say (Dana / Thomas):**
> Every field Piper and Hunter wrote is in the CRM, not in a warehouse model or a rep's ChatGPT tab. That's what moves field completeness up from under 25% and gives Finance a rollup it can use.

---

## 5 · Close: why the two belong in one flow (2 min)

1. **Piper proves the pattern** on one owner, in conversation, at 10:15 PM.
2. **That confirmed record becomes the template.**
3. **Hunter applies it across the state** over days, which is what the long-horizon runtime is for.
4. **Marcus's reps work a ranked list of named owners**, and every step is written back to Salesforce.

**Value (Nina / Thomas):**
> At about $2,700 per location, the $605K program pays for itself at around 225 locations. Colorado alone surfaced 600 dark locations controlled by owners Yelp already bills. That's more than two and a half times the payback threshold in a single pilot state, before Piper's inbound and before the next territory.

**Name the gap (scores in Cert 1):**
> One thing we haven't covered: everything today is acquisition. Paying locations are also falling because of churn, and nobody in discovery has raised Service, Success or retention. I'd like 30 minutes with Alisha, and with Thomas on the pilot gate, so we can cover the Keep half of this map.

---

## Likely questions

| Question | Answer |
|---|---|
| *Priya:* "My chat tool renews in March." | "Piper runs alongside it; a pilot on the after-hours window doesn't touch the renewal. Measure speed to lead and multi-location discovery rate side by side." |
| *Dana:* "Will this eat our API limits?" | "The routing is a record-triggered Flow, on-platform. Hunter's reads are batched by the runtime. Neither is an external script hammering the API." |
| *Dana:* "Is using billing data OK?" | "It stays inside Yelp's Salesforce trust boundary. Lookups and writes are logged through the Einstein Trust Layer, and governance on which fields agents can read is admin-controlled." |
| "When can we have Hunter?" | "It's not GA and we're not committing to a date. I can put you on the beta waitlist; I can't promise acceptance." |
| *Marcus:* "What if Hunter's wrong about an owner?" | "Every operator carries a confidence score and the evidence behind it. Reps confirm on the first call, and corrections become training signal." |
| *Thomas:* "How do I gate a pilot?" | "One territory, one metric: dark locations activated per month among Hunter-identified operators, against the 225-location payback line." |

---

## Map to the lifecycle diagram

| Diagram box | Where it shows up |
|---|---|
| **Agentic Marketing (Piper)** | Section 1: after-hours qualification on Yelp for Business |
| **Prospecting (Hunter)** | Section 3: operator discovery across billing and other signals |
| **SDR Agent (Hunter)** | Section 3, step 6: sequences against 600 dark locations |
| **GTM Engineering (Flow)** | Section 2: `Yelp - Multi-Location Lead Routing` |
| **Win** | Sections 4–5: routed reps, briefs, opportunities, value math |
