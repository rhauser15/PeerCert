"""Seed (or reset) the Find & Win demo records in the Salesforce org.

  python3 scripts/seed.py            # reset, then load Hunter accounts + Piper lead
  python3 scripts/seed.py --piper    # reset and reload only the Piper lead (fires the routing Flow live)
  python3 scripts/seed.py --reset    # delete demo records only

Every record is tagged (Agent_Source__c or a "Hunter" name prefix), and reset deletes only tagged records.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
import demo_data  # noqa: E402

ORG = os.environ.get("SF_ORG", "trailsignup-429cdf")
CAMPAIGN = "Hunter - Colorado Dark Location Outreach"


def sf(*args, check=True):
    r = subprocess.run(["sf", *args, "-o", ORG, "--json"], capture_output=True, text=True)
    out = json.loads(r.stdout or "{}")
    if check and out.get("status") not in (0, None):
        sys.exit(f"sf {' '.join(args[:3])} failed:\n{json.dumps(out, indent=1)[:3000]}")
    return out


def query(soql):
    return sf("data", "query", "-q", soql)["result"]["records"]


def apex(code):
    with tempfile.NamedTemporaryFile("w", suffix=".apex", delete=False) as f:
        f.write(code)
    out = sf("apex", "run", "--file", f.name)
    os.unlink(f.name)
    if not out["result"].get("success"):
        sys.exit(out["result"].get("exceptionMessage") or out["result"].get("compileProblem"))


def reset(piper_only=False):
    print("Deleting existing demo records...")
    code = "delete [SELECT Id FROM Lead WHERE Agent_Source__c = 'Piper'];\n"
    if not piper_only:
        code += (
            "delete [SELECT Id FROM Task WHERE Subject LIKE 'Hunter brief:%'];\n"
            f"delete [SELECT Id FROM Campaign WHERE Name = '{CAMPAIGN}'];\n"
            "delete [SELECT Id FROM Account WHERE Agent_Source__c IN ('Hunter','Self-Serve Checkout') "
            "AND Yelp_Segment__c != null];\n"
        )
    apex(code)


def rec(sobject, ref, **fields):
    return {"attributes": {"type": sobject, "referenceId": ref}, **fields}


def import_plan(steps):
    """steps: list of (sobject, [records]). Writes a tree plan and imports it."""
    d = tempfile.mkdtemp(prefix="yelp-seed-")
    plan = []
    for n, (sobject, records) in enumerate(steps):
        for c in range(0, len(records), 200):
            fname = f"{n:02d}_{sobject}_{c // 200}.json"
            with open(os.path.join(d, fname), "w") as f:
                json.dump({"records": records[c:c + 200]}, f)
            plan.append({"sobject": sobject, "saveRefs": True, "resolveRefs": True, "files": [fname]})
    with open(os.path.join(d, "plan.json"), "w") as f:
        json.dump(plan, f)
    out = sf("data", "import", "tree", "--plan", os.path.join(d, "plan.json"))
    print(f"  imported {len(out['result'])} records")


def ids():
    users = {u["Alias"]: u["Id"] for u in query(
        "SELECT Id, Alias FROM User WHERE Alias IN ('ccentral','vwest','bill','vcent') AND IsActive = true")}
    rts = {r["DeveloperName"]: r["Id"] for r in query(
        "SELECT Id, DeveloperName FROM RecordType WHERE DeveloperName IN "
        "('SDO_Account_Simple','SDO_Lead_Default','SimpleOpportunity')")}
    return users, rts


def seed_hunter(data, users, rts):
    print("Loading Hunter operators, locations, contacts, opportunities, briefs...")
    today = dt.date.today()
    parents, children, contacts, opps, tasks, members = [], [], [], [], [], []
    for op in data["operators"]:
        r = op["rank"]
        owner = users[op["rep_alias"]]
        parents.append(rec(
            "Account", f"Op{r}", Name=op["name"], RecordTypeId=rts["SDO_Account_Simple"], OwnerId=owner,
            Type="Prospect", Phone=op["phone"], BillingCity=op["city"], BillingState="Colorado",
            BillingCountry="United States", Yelp_Segment__c="Multi-Location", Agent_Source__c="Hunter",
            Hunter_Rank__c=r, Hunter_Confidence__c=op["confidence"], Location_Count__c=op["location_count"],
            Paying_Locations__c=op["paying"], Dark_Locations__c=op["dark"], Brand_Count__c=len(op["brands"]),
            Brands_Operated__c="; ".join(op["brands"]), Monthly_Ad_Spend__c=op["monthly_spend"],
            Unrealized_Annual_Spend__c=op["unrealized_annual"],
            Hunter_Signals__c="\n".join(f"{s['label']}: {s['detail']}" for s in op["signals"]),
            Description=f"Operator hierarchy built by Hunter. {op['location_count']} locations, "
                        f"{len(op['brands'])} brands. Rank #{r} in Colorado by unrealized spend."))
        for j, loc in enumerate(op["locations"]):
            dark = loc["status"] == "Dark"
            children.append(rec(
                "Account", f"Op{r}L{j}", Name=loc["name"], ParentId=f"@Op{r}",
                RecordTypeId=rts["SDO_Account_Simple"], OwnerId=owner, Phone=loc["phone"],
                BillingCity=loc["city"], BillingState="Colorado", BillingCountry="United States",
                Brand__c=loc["brand"], Location_Status__c=loc["status"], Monthly_Ad_Spend__c=loc["monthly"],
                Yelp_Segment__c="Self-Serve", Agent_Source__c="Hunter" if dark else "Self-Serve Checkout",
                Location_Count__c=1, Paying_Locations__c=0 if dark else 1, Dark_Locations__c=1 if dark else 0))
        contacts.append(rec(
            "Contact", f"C{r}", FirstName=op["first"], LastName=op["last"], Title=op["title"],
            Email=op["email"], Phone=op["phone"], AccountId=f"@Op{r}", OwnerId=owner,
            Description="Principal identified by Hunter (entity + registered agent data, billing contact)."))
        tasks.append(rec(
            "Task", f"T{r}", Subject=f"Hunter brief: {op['name']} ({op['location_count']} locations, "
                                   f"{op['dark']} dark)",
            WhatId=f"@Op{r}", WhoId=f"@C{r}", OwnerId=owner, Priority="High" if r <= 10 else "Normal",
            Status="Not Started", ActivityDate=str(today + dt.timedelta(days=1 + r % 3)),
            Description=op["brief"]))
        members.append(rec("CampaignMember", f"M{r}", CampaignId="@Camp", ContactId=f"@C{r}", Status="Sent"))
        if r <= 10:
            opps.append(rec(
                "Opportunity", f"O{r}", Name=f"{op['name']} - Multi-Location Activation ({op['dark']} dark)",
                AccountId=f"@Op{r}", OwnerId=owner, RecordTypeId=rts["SimpleOpportunity"],
                StageName="Qualification", Amount=op["unrealized_annual"],
                CloseDate=str(today + dt.timedelta(days=45 + r * 3)), Type="New Business",
                NextStep="Hunter brief sent; book multi-location review",
                Description=f"Activate {op['dark']} dark locations and consolidate {op['paying']} "
                            f"self-serve accounts into one multi-location package."))
    campaign = [rec("Campaign", "Camp", Name=CAMPAIGN, Type="Email", Status="In Progress", IsActive=True,
                    StartDate=str(today - dt.timedelta(days=2)),
                    Description=f"Hunter outbound sequences against {data['territory']['dark_locations']} "
                                f"dark locations controlled by {data['territory']['operators']} Colorado "
                                f"operators. Principals of the top 40 operators shown as members.")]
    import_plan([("Account", parents), ("Account", children), ("Contact", contacts), ("Campaign", campaign),
                 ("CampaignMember", members), ("Opportunity", opps), ("Task", tasks)])


def seed_piper(data, users, rts):
    print("Loading Piper lead (routing Flow fires on insert) and Thursday meeting...")
    p = data["piper"]
    tz = ZoneInfo("America/Denver")
    today = dt.date.today()
    thursday = today + dt.timedelta(days=(3 - today.weekday()) % 7 or 7)
    start = dt.datetime.combine(thursday, dt.time(10, 0), tz).astimezone(dt.timezone.utc)
    lead = rec(
        "Lead", "Piper1", FirstName=p["first_name"], LastName=p["last_name"], Title=p["title"],
        Company=p["company"], Email=p["email"], Phone=p["phone"], City=p["city"], State="Colorado",
        Country="United States", LeadSource="Web", RecordTypeId=rts["SDO_Lead_Default"],
        Agent_Source__c="Piper", Location_Count__c=p["locations"], Brand_Count__c=len(p["brands"]),
        Brands_Operated__c="; ".join(f"{v} {k}" for k, v in p["brand_breakdown"].items()),
        Operates_Other_Brands__c=True, Self_Serve_Monthly_Spend__c=p["monthly_spend"],
        Unrealized_Annual_Spend__c=p["unrealized_annual"], Committed_Future_Locations__c=p["future_locations"],
        Development_Rights_Through__c=p["rights_through"], Agent_Qualification_Summary__c=p["summary"],
        Description=f"Signed up via self-serve checkout for {p['signed_up_for']} at ${p['monthly_spend']}/mo.")
    event = rec(
        "Event", "Ev1", Subject=f"Intro: {p['company']} - 12-location plan (booked by Piper)",
        WhoId="@Piper1", OwnerId=users[p["rep_alias"]], StartDateTime=start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        EndDateTime=(start + dt.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        Location="Zoom", Description=p["summary"])
    import_plan([("Lead", [lead]), ("Event", [event])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="delete demo records only")
    ap.add_argument("--piper", action="store_true", help="reset and reload only the Piper lead")
    a = ap.parse_args()
    data = demo_data.build()
    reset(piper_only=a.piper)
    if a.reset:
        return
    users, rts = ids()
    if not a.piper:
        seed_hunter(data, users, rts)
    seed_piper(data, users, rts)
    print("Done.")


if __name__ == "__main__":
    main()
