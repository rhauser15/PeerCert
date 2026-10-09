"""Generates the custom field metadata for the Find & Win demo."""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "force-app", "main", "default", "objects")

def num(label, desc, scale=0, precision=6):
    return f"<type>Number</type><precision>{precision}</precision><scale>{scale}</scale>", label, desc

def cur(label, desc):
    return "<type>Currency</type><precision>12</precision><scale>0</scale>", label, desc

def chk(label, desc):
    return "<type>Checkbox</type><defaultValue>false</defaultValue>", label, desc

def txt(label, desc, length=255):
    return f"<type>Text</type><length>{length}</length>", label, desc

def lta(label, desc, lines=6):
    return f"<type>LongTextArea</type><length>32768</length><visibleLines>{lines}</visibleLines>", label, desc

def pick(label, desc, values):
    vals = "".join(
        f"<value><fullName>{v}</fullName><default>false</default><label>{v}</label></value>" for v in values
    )
    return (
        "<type>Picklist</type><valueSet><restricted>true</restricted>"
        f"<valueSetDefinition><sorted>false</sorted>{vals}</valueSetDefinition></valueSet>"
    ), label, desc

AGENT_SOURCES = ["Piper", "Hunter", "Self-Serve Checkout"]
SEGMENTS = ["Self-Serve", "Local", "Emerging", "Multi-Location", "Enterprise"]

FIELDS = {
    "Lead": {
        "Location_Count__c": num("Location Count", "Total locations the owner operates, across all brands."),
        "Brand_Count__c": num("Brand Count", "Distinct brands the owner operates."),
        "Brands_Operated__c": txt("Brands Operated", "Brands the owner operates, semicolon separated."),
        "Operates_Other_Brands__c": chk("Operates Other Brands", "Owner operates locations under brands other than the one that signed up."),
        "Multi_Location__c": chk("Multi-Location", "Set by the routing Flow when the owner controls 3+ locations or multiple brands."),
        "Agent_Source__c": pick("Agent Source", "Which agent created or qualified this record.", AGENT_SOURCES),
        "Self_Serve_Monthly_Spend__c": cur("Self-Serve Monthly Spend", "Monthly ad spend selected at self-serve checkout."),
        "Unrealized_Annual_Spend__c": cur("Unrealized Annual Spend", "Annual revenue at Yelp average per location across locations not yet advertising."),
        "Committed_Future_Locations__c": num("Committed Future Locations", "Locations under development rights not yet open."),
        "Development_Rights_Through__c": num("Development Rights Through", "Year the owner's development rights run through.", precision=4),
        "Agent_Qualification_Summary__c": lta("Agent Qualification Summary", "What the agent learned in conversation."),
        "Routing_Reason__c": txt("Routing Reason", "Why the routing Flow sent this lead to a rep."),
    },
    "Account": {
        "Location_Count__c": num("Location Count", "Total locations controlled by this operator."),
        "Paying_Locations__c": num("Paying Locations", "Locations already advertising (usually self-serve)."),
        "Dark_Locations__c": num("Dark Locations", "Locations the operator controls that are not advertising."),
        "Brand_Count__c": num("Brand Count", "Distinct brands operated."),
        "Brands_Operated__c": txt("Brands Operated", "Brands operated, semicolon separated."),
        "Brand__c": txt("Brand", "Brand of this individual location.", 80),
        "Location_Status__c": pick("Location Status", "Whether this location is advertising.", ["Paying - Self-Serve", "Paying - Managed", "Dark"]),
        "Monthly_Ad_Spend__c": cur("Monthly Ad Spend", "Current monthly ad spend."),
        "Unrealized_Annual_Spend__c": cur("Unrealized Annual Spend", "Dark locations x Yelp average revenue per location."),
        "Hunter_Rank__c": num("Hunter Rank", "Operator rank by unrealized spend in the territory."),
        "Hunter_Confidence__c": num("Hunter Confidence %", "Confidence that these locations share one operator.", precision=3),
        "Hunter_Signals__c": lta("Hunter Signals", "Evidence Hunter used to connect these locations."),
        "Yelp_Segment__c": pick("Yelp Segment", "Sales segment.", SEGMENTS),
        "Agent_Source__c": pick("Agent Source", "Which agent created or qualified this record.", AGENT_SOURCES),
    },
}

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>
    <label>{label}</label>
    <description>{desc}</description>
    <inlineHelpText>{desc}</inlineHelpText>
    {body}
</CustomField>
"""

for obj, fields in FIELDS.items():
    d = os.path.join(ROOT, obj, "fields")
    os.makedirs(d, exist_ok=True)
    for name, (body, label, desc) in fields.items():
        with open(os.path.join(d, f"{name}.field-meta.xml"), "w") as f:
            f.write(TEMPLATE.format(name=name, label=label, desc=desc, body=body))
    print(obj, len(fields))

# --- Permission set: field access for everything above ---
MD = os.path.join(ROOT, "..")
perms = []
for obj, fields in FIELDS.items():
    for name in fields:
        perms.append(
            f"    <fieldPermissions><editable>true</editable><field>{obj}.{name}</field><readable>true</readable></fieldPermissions>"
        )
os.makedirs(os.path.join(MD, "permissionsets"), exist_ok=True)
with open(os.path.join(MD, "permissionsets", "Yelp_Find_Win.permissionset-meta.xml"), "w") as f:
    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Yelp Find and Win Demo</label>
    <description>Access to Piper and Hunter fields for the Yelp Find and Win demo.</description>
    <hasActivationRequired>false</hasActivationRequired>
{chr(10).join(perms)}
</PermissionSet>
""")

# --- List views ---
def list_view(obj, name, label, columns, filters, sort=None):
    cols = "".join(f"\n    <columns>{c}</columns>" for c in columns)
    flt = "".join(
        f"\n    <filters><field>{fld}</field><operation>{op}</operation><value>{val}</value></filters>"
        for fld, op, val in filters
    )
    d = os.path.join(ROOT, obj, "listViews")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{name}.listView-meta.xml"), "w") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>{name}</fullName>{cols}
    <filterScope>Everything</filterScope>{flt}
    <label>{label}</label>
</ListView>
""")

list_view("Lead", "Piper_Multi_Location_Leads", "Piper - Multi-Location Leads",
    ["FULL_NAME", "LEAD.COMPANY", "Location_Count__c", "Brand_Count__c", "Brands_Operated__c",
     "Unrealized_Annual_Spend__c", "Routing_Reason__c", "CORE.USERS.ALIAS", "LEAD.CREATED_DATE"],
    [("Multi_Location__c", "equals", "1")])
list_view("Account", "Hunter_Colorado_Operators", "Hunter - Colorado Operators (Ranked)",
    ["Hunter_Rank__c", "ACCOUNT.NAME", "Location_Count__c", "Paying_Locations__c", "Dark_Locations__c",
     "Brands_Operated__c", "Unrealized_Annual_Spend__c", "Hunter_Confidence__c", "CORE.USERS.ALIAS"],
    [("Agent_Source__c", "equals", "Hunter"), ("Hunter_Rank__c", "greaterThan", "0")])
list_view("Account", "Hunter_Dark_Locations", "Hunter - Dark Locations (In Sequence)",
    ["ACCOUNT.NAME", "Brand__c", "ACCOUNT.ADDRESS1_CITY", "Location_Status__c"],
    [("Location_Status__c", "equals", "Dark")])
print("permset + list views")
