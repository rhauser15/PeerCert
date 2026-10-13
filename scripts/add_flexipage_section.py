"""Adds a 'Yelp Agent Signals' Dynamic Forms section to the Sales for Tech Account record page.

The section is the first thing on the Details tab and only shows on demo accounts (Location_Count__c > 0),
so other demos in the org don't see it.
"""
import os

PATH = os.path.join(os.path.dirname(__file__), "..", "force-app", "main", "default", "flexipages",
                    "Tech_Account_Data_Cloud_3_Panel.flexipage-meta.xml")
DETAILS_FACET = "Facet-526ee946-86fd-4fcf-a09a-569f73327dad"  # holds the Details tab's field sections
LEFT = ["Agent_Source__c", "Yelp_Segment__c", "Hunter_Rank__c", "Hunter_Confidence__c", "Brand__c",
        "Location_Status__c", "Monthly_Ad_Spend__c"]
RIGHT = ["Location_Count__c", "Paying_Locations__c", "Dark_Locations__c", "Brand_Count__c",
         "Brands_Operated__c", "Unrealized_Annual_Spend__c", "Hunter_Signals__c"]


def fields_region(name, fields):
    items = "".join(f"""
        <itemInstances>
            <fieldInstance>
                <fieldInstanceProperties><name>uiBehavior</name><value>none</value></fieldInstanceProperties>
                <fieldItem>Record.{f}</fieldItem>
                <identifier>Record{f.replace('__c', '')}Field_yelp</identifier>
            </fieldInstance>
        </itemInstances>""" for f in fields)
    return f"""    <flexiPageRegions>{items}
        <name>{name}</name>
        <type>Facet</type>
    </flexiPageRegions>
"""


COLUMNS = """    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties><name>body</name><value>Facet-yelp-left</value></componentInstanceProperties>
                <componentName>flexipage:column</componentName>
                <identifier>flexipage_column_yelp_left</identifier>
            </componentInstance>
        </itemInstances>
        <itemInstances>
            <componentInstance>
                <componentInstanceProperties><name>body</name><value>Facet-yelp-right</value></componentInstanceProperties>
                <componentName>flexipage:column</componentName>
                <identifier>flexipage_column_yelp_right</identifier>
            </componentInstance>
        </itemInstances>
        <name>Facet-yelp-columns</name>
        <type>Facet</type>
    </flexiPageRegions>
"""

SECTION = """        <itemInstances>
            <componentInstance>
                <componentInstanceProperties><name>columns</name><value>Facet-yelp-columns</value></componentInstanceProperties>
                <componentInstanceProperties><name>horizontalAlignment</name><value>false</value></componentInstanceProperties>
                <componentInstanceProperties><name>label</name><value>Yelp Agent Signals</value></componentInstanceProperties>
                <componentName>flexipage:fieldSection</componentName>
                <identifier>flexipage_fieldSection_yelp</identifier>
                <visibilityRule>
                    <criteria>
                        <leftValue>{!Record.Location_Count__c}</leftValue>
                        <operator>GT</operator>
                        <rightValue>0</rightValue>
                    </criteria>
                </visibilityRule>
            </componentInstance>
        </itemInstances>
"""

s = open(PATH).read()
if "Yelp Agent Signals" in s:
    print("already present")
else:
    marker = f"        <name>{DETAILS_FACET}</name>"
    region_start = s.rfind("    <flexiPageRegions>\n", 0, s.index(marker))
    first_item = s.index("        <itemInstances>", region_start)
    s = s[:first_item] + SECTION + s[first_item:]
    new_regions = fields_region("Facet-yelp-left", LEFT) + fields_region("Facet-yelp-right", RIGHT) + COLUMNS
    s = s[:region_start] + new_regions + s[region_start:]
    open(PATH, "w").write(s)
    print("added")
