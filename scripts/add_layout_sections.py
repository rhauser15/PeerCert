"""Inserts a 'Yelp Agent Signals' section as the second section of the Lead and Account layouts."""
import os, re, sys

BASE = os.path.join(os.path.dirname(__file__), "..", "force-app", "main", "default", "layouts")
SECTIONS = {
    "Lead-Tech - Lead.layout-meta.xml": (
        ["Agent_Source__c", "Location_Count__c", "Brand_Count__c", "Brands_Operated__c",
         "Committed_Future_Locations__c", "Development_Rights_Through__c"],
        ["Multi_Location__c", "Operates_Other_Brands__c", "Self_Serve_Monthly_Spend__c",
         "Unrealized_Annual_Spend__c", "Routing_Reason__c"],
        ["Agent_Qualification_Summary__c"],
    ),
    "Account-Tech - Account.layout-meta.xml": (
        ["Agent_Source__c", "Yelp_Segment__c", "Hunter_Rank__c", "Hunter_Confidence__c",
         "Brand__c", "Location_Status__c", "Monthly_Ad_Spend__c"],
        ["Location_Count__c", "Paying_Locations__c", "Dark_Locations__c", "Brand_Count__c",
         "Brands_Operated__c", "Unrealized_Annual_Spend__c"],
        ["Hunter_Signals__c"],
    ),
}

def column(fields):
    items = "".join(
        f"\n            <layoutItems>\n                <behavior>Edit</behavior>\n                <field>{f}</field>\n            </layoutItems>"
        for f in fields
    )
    return f"\n        <layoutColumns>{items}\n        </layoutColumns>"

for fname, (left, right, wide) in SECTIONS.items():
    path = os.path.join(BASE, fname)
    xml = open(path).read()
    if "Yelp Agent Signals" in xml:
        print("already present:", fname); continue
    two_col = f"""    <layoutSections>
        <customLabel>true</customLabel>
        <detailHeading>true</detailHeading>
        <editHeading>true</editHeading>
        <label>Yelp Agent Signals</label>{column(left)}{column(right)}
        <style>TwoColumnsTopToBottom</style>
    </layoutSections>
    <layoutSections>
        <customLabel>true</customLabel>
        <detailHeading>false</detailHeading>
        <editHeading>false</editHeading>
        <label>Yelp Agent Evidence</label>{column(wide)}
        <style>OneColumn</style>
    </layoutSections>
"""
    # insert after the first </layoutSections>
    idx = xml.index("</layoutSections>") + len("</layoutSections>\n")
    xml = xml[:idx] + two_col + xml[idx:]
    open(path, "w").write(xml)
    print("updated:", fname)
