"""Single source of truth for the Find & Win demo data.

Used by seed.py (Salesforce records) and by `python3 scripts/demo_data.py`, which writes
prototypes/data.js so the Piper and Hunter mockups show exactly what lands in the CRM.
"""
import json
import os
import random

ORG_URL = "https://trailsignup-429cdfd78ec835.lightning.force.com"
REV_PER_LOCATION = 2700  # Yelp revenue per paying advertising location, per year (case study)
SELF_SERVE_MONTHLY = 225  # ~ $2,700 / 12

# Territory-wide results Hunter reports for the Colorado pilot (from the demo narrative).
TERRITORY = {
    "state": "Colorado",
    "operators": 400,
    "locations": 1700,
    "paying_locations": 1100,
    "dark_locations": 600,
    "unrealized_annual": 600 * REV_PER_LOCATION,  # $1.62M
    "routed_to_reps": 40,
    "pages_scanned": 10412,
    "selfserve_accounts_scanned": 3870,
}

# Piper's inbound conversation: the owner who proves the pattern.
PIPER_LEAD = {
    "first_name": "Sam",
    "last_name": "Whitaker",
    "title": "Owner / Franchisee",
    "company": "Whitaker Hospitality Group",
    "email": "sam@whitakerhospitality.example.com",
    "phone": "(720) 555-0142",
    "city": "Lakewood",
    "state": "CO",
    "signed_up_for": "Smoothie King - Lakewood (Belmar)",
    "signup_time": "Tuesday, 10:15 PM",
    "monthly_spend": 300,
    "reviews": 60,
    "opened": 2024,
    "locations": 12,
    "brands": ["Dave's Hot Chicken", "Jersey Mike's Subs", "Smoothie King"],
    "brand_breakdown": {"Dave's Hot Chicken": 7, "Jersey Mike's Subs": 4, "Smoothie King": 1},
    "markets": "Denver metro and Colorado Springs",
    "future_locations": 4,
    "rights_through": 2028,
    "rep_alias": "ccentral",
}
PIPER_LEAD["annual_as_signed"] = PIPER_LEAD["monthly_spend"] * 12  # $3,600
PIPER_LEAD["annual_potential"] = PIPER_LEAD["locations"] * REV_PER_LOCATION  # $32,400
PIPER_LEAD["unrealized_annual"] = (PIPER_LEAD["locations"] - 1) * REV_PER_LOCATION  # $29,700
PIPER_LEAD["summary"] = (
    "Piper conversation, Tuesday 10:15 PM, Yelp for Business checkout.\n"
    "Signed up to advertise one Smoothie King (Lakewood, Belmar) at $300/month. Self-serve signals: "
    "1 location, 60 reviews, opened 2024.\n"
    "Piper asked: 'Is this your only location, or do you operate others?'\n"
    "Owner operates 12 locations across 3 brands: 7 Dave's Hot Chicken, 4 Jersey Mike's Subs, "
    "1 Smoothie King, in Denver metro and Colorado Springs. Controls one marketing budget himself. "
    "Holds development rights for 4 more locations through 2028.\n"
    "Why Yelp missed him: the 12 pages share no name (brand matching returns nothing) and each is "
    "claimed by a store manager with a store email. His name is on none of them.\n"
    "Value: $3,600/yr as signed. ~$32,400/yr across 12 locations at Yelp average; 16 locations by 2028.\n"
    "Next step: intro with Multi-Location rep booked for Thursday 10:00 AM MT."
)

BRANDS = [
    "Dave's Hot Chicken", "Jersey Mike's Subs", "Smoothie King", "Wingstop", "Crumbl Cookies",
    "Tropical Smoothie Cafe", "Firehouse Subs", "Jimmy John's", "Ziggi's Coffee", "Teriyaki Madness",
    "Marco's Pizza", "Nothing Bundt Cakes", "Scooter's Coffee", "Rush Bowls", "Rocky Mountain Chocolate Factory",
]
CITIES = [
    ("Denver", "303"), ("Aurora", "720"), ("Lakewood", "303"), ("Littleton", "303"), ("Centennial", "720"),
    ("Highlands Ranch", "720"), ("Parker", "720"), ("Castle Rock", "303"), ("Arvada", "303"),
    ("Westminster", "303"), ("Thornton", "720"), ("Broomfield", "720"), ("Boulder", "303"),
    ("Longmont", "303"), ("Fort Collins", "970"), ("Loveland", "970"), ("Greeley", "970"),
    ("Colorado Springs", "719"), ("Pueblo", "719"), ("Golden", "303"), ("Lone Tree", "720"),
]
CENTERS = [
    "Belmar", "Southlands", "Park Meadows", "Flatiron Crossing", "Promenade Shops at Briargate",
    "Orchard Town Center", "Twenty Ninth Street", "Front Range Village", "Streets at SouthGlenn",
    "Colorado Mills", "Chapel Hills", "Northfield Stapleton",
]
OPERATOR_NAMES = [
    "Front Range Franchise Partners", "Peak Provisions Group", "Mile High QSR Holdings", "Summit Brands Colorado",
    "Centennial Eats", "Red Rocks Restaurant Group", "Pikes Peak Food Co.", "Cherry Creek Hospitality",
    "Foothills Franchise Co.", "Blue Spruce Brands", "Columbine Restaurant Partners", "Platte River Eats",
    "Aspen Ridge Hospitality", "High Plains QSR", "Longs Peak Brands", "Bear Creek Franchise Group",
    "Sangre Holdings", "Clear Creek Eats", "Monarch Restaurant Group", "Golden Spike Hospitality",
    "Elk Ridge Brands", "Larkspur Food Group", "Arapahoe Eats Collective", "Silver Plume Partners",
    "Granite Peak Hospitality", "Crestone Brands", "Timberline QSR", "Big Thompson Restaurant Co.",
    "Fourteener Franchise Group", "Mesa Verde Eats", "Juniper Lane Hospitality", "Highline Canal Brands",
    "Saddleback Restaurant Group", "Canyon Wind Eats", "Sunlight Peak Holdings", "Tabletop Franchise Co.",
    "Wildflower Brands", "Quarry Street Hospitality", "Ute Pass Restaurant Group", "Larimer Square Eats",
]
FIRST = ["Priya", "Daniel", "Monica", "Luis", "Jenna", "Andre", "Kim", "Tomas", "Rachel", "Omar", "Beth",
         "Hector", "Nadia", "Grant", "Lena", "Victor", "Carla", "Devin", "Aisha", "Wes"]
LAST = ["Patel", "Nguyen", "Alvarez", "Brooks", "Kowalski", "Haddad", "Ortiz", "Lindqvist", "Okafor", "Reyes",
        "Sutton", "Moreno", "Chen", "Fischer", "Kaur", "Delgado", "Novak", "Barrett", "Ibrahim", "Larsen"]
REPS = ["ccentral", "vwest", "bill", "vcent"]


def _signals(rng, op, locs, brands):
    paying = [l for l in locs if l["status"] != "Dark"]
    n_pay = max(2, min(len(paying), rng.randint(3, 6)))
    card = rng.randint(1000, 9999)
    center = rng.choice(CENTERS)
    phone_n = rng.randint(3, min(8, len(locs)))
    sigs = [
        {"type": "billing", "label": "Shared payment method",
         "detail": f"Same card (Visa ending {card}) pays {n_pay} self-serve accounts across {min(len(brands), n_pay)} brands"},
        {"type": "billing", "label": "Shared billing contact",
         "detail": f"Billing contact {op['email']} on {max(2, n_pay - 1)} accounts"},
        {"type": "phone", "label": "Phone routing",
         "detail": f"{op['phone']} forwards from {phone_n} pages in different brands"},
        {"type": "reviews", "label": "Same review responder",
         "detail": f"'{op['first']} {op['last'][0]}.' replies to reviews on {min(len(brands), 3)} unrelated brands"},
        {"type": "colocation", "label": "Co-located openings",
         "detail": f"{rng.randint(2, 3)} brands opened within 9 months at {center}"},
        {"type": "entity", "label": "Entity + registered agent (Data Vendor Gateway)",
         "detail": f"{len(locs)} Colorado LLCs share registered agent and principal address; managing member {op['first']} {op['last']}"},
    ]
    k = rng.randint(4, 6)
    return sigs[:2] + rng.sample(sigs[2:], k - 2)


def build():
    rng = random.Random(20261008)
    operators = []
    for i, name in enumerate(OPERATOR_NAMES):
        first, last = FIRST[i % len(FIRST)], LAST[(i * 7) % len(LAST)]
        slug = "".join(c for c in name.lower() if c.isalnum())[:18]
        n_brands = rng.choice([2, 2, 3, 3, 3, 4])
        brands = rng.sample(BRANDS, n_brands)
        n_locs = rng.randint(6, 18) if i < 15 else rng.randint(4, 11)
        home_cities = rng.sample(CITIES, min(len(CITIES), rng.randint(3, 7)))
        area = home_cities[0][1]
        op = {
            "name": name, "first": first, "last": last, "title": "Owner / Managing Member",
            "email": f"{first.lower()}@{slug}.example.com",
            "phone": f"({area}) 555-01{rng.randint(10, 99)}",
            "city": home_cities[0][0], "brands": brands,
        }
        locs = []
        for j in range(n_locs):
            brand = brands[j % n_brands]
            city, ac = rng.choice(home_cities)
            locs.append({"brand": brand, "city": city, "name": f"{brand} - {city}",
                         "phone": f"({ac}) 555-01{rng.randint(10, 99)}"})
        # Dedupe names (two same-brand stores in a city get a center suffix)
        seen = {}
        for l in locs:
            seen[l["name"]] = seen.get(l["name"], 0) + 1
            if seen[l["name"]] > 1:
                l["name"] += f" ({rng.choice(CENTERS)})"
        dark_share = rng.uniform(0.3, 0.65)
        n_dark = max(1, round(n_locs * dark_share))
        for idx, l in enumerate(locs):
            if idx >= n_locs - n_dark:
                l["status"], l["monthly"] = "Dark", 0
            else:
                l["status"], l["monthly"] = "Paying - Self-Serve", rng.choice([150, 200, 225, 250, 300])
        op["locations"] = locs
        op["location_count"] = n_locs
        op["paying"] = n_locs - n_dark
        op["dark"] = n_dark
        op["monthly_spend"] = sum(l["monthly"] for l in locs)
        op["unrealized_annual"] = n_dark * REV_PER_LOCATION
        op["confidence"] = rng.randint(84, 99)
        op["signals"] = _signals(rng, op, locs, brands)
        operators.append(op)

    operators.sort(key=lambda o: (-o["unrealized_annual"], -o["location_count"]))
    for rank, op in enumerate(operators, 1):
        op["rank"] = rank
        op["rep_alias"] = REPS[(rank - 1) % len(REPS)]
        op["brief"] = brief(op)
    top = {
        "operators": len(operators),
        "locations": sum(o["location_count"] for o in operators),
        "paying": sum(o["paying"] for o in operators),
        "dark": sum(o["dark"] for o in operators),
        "unrealized_annual": sum(o["unrealized_annual"] for o in operators),
    }
    return {"org_url": ORG_URL, "rev_per_location": REV_PER_LOCATION, "territory": TERRITORY, "top40": top,
            "piper": PIPER_LEAD, "operators": operators}


def brief(op):
    sig_lines = "\n".join(f"- {s['label']}: {s['detail']}" for s in op["signals"])
    return (
        f"Hunter brief: {op['name']} (rank #{op['rank']} in Colorado)\n"
        f"Principal: {op['first']} {op['last']}, {op['title']} | {op['email']} | {op['phone']}\n\n"
        f"Controls {op['location_count']} locations across {len(op['brands'])} brands "
        f"({', '.join(op['brands'])}). {op['paying']} already pay self-serve "
        f"(${op['monthly_spend']:,}/mo combined, billed as unrelated accounts). {op['dark']} are dark.\n"
        f"Unrealized: ${op['unrealized_annual']:,}/yr at Yelp average revenue per location.\n\n"
        f"Why Hunter thinks this is one operator ({op['confidence']}% confidence):\n{sig_lines}\n\n"
        f"Pattern match: same shape as Whitaker Hospitality (confirmed by Piper): multi-brand franchisee, "
        f"pages claimed by store managers, owner on none of them.\n\n"
        f"Suggested opener: \"{op['first']}, you're already advertising {op['paying']} of your locations with us "
        f"on separate self-serve plans. We'd like to show you all {op['location_count']} in one view and what "
        f"the other {op['dark']} could be doing.\"\n"
        f"Next step: book a multi-location review and propose one package across all locations."
    )


if __name__ == "__main__":
    data = build()
    root = os.path.join(os.path.dirname(__file__), "..")
    os.makedirs(os.path.join(root, "prototypes"), exist_ok=True)
    with open(os.path.join(root, "prototypes", "data.js"), "w") as f:
        f.write("// Generated by scripts/demo_data.py. Do not edit by hand.\n")
        f.write("window.YELP_DATA = " + json.dumps(data, indent=1) + ";\n")
    t = data["top40"]
    print(f"top 40: {t['locations']} locations, {t['paying']} paying, {t['dark']} dark, ${t['unrealized_annual']:,}")
    for o in data["operators"][:5]:
        print(o["rank"], o["name"], o["location_count"], o["dark"], o["unrealized_annual"], o["brands"])
