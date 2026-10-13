"""Generates the Find & Win leadership reports and dashboard metadata."""
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "force-app", "main", "default")
FOLDER = "Yelp_Find_and_Win"
RUNNING_USER = "trailsignup.429cdfd78ec835@salesforce.com"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + text.strip() + "\n")


def crit(col, op, val):
    return f"<criteriaItems><column>{col}</column><columnToColumn>false</columnToColumn><isUnlocked>true</isUnlocked><operator>{op}</operator><value>{val}</value></criteriaItems>"


def report(name, label, rtype, cols, criteria, group, sort_by=None, date_col="CREATED_DATE", desc="", scope="organization", formulas=()):
    columns = "".join(
        f"<columns>{''.join(f'<aggregateTypes>{a}</aggregateTypes>' for a in aggs)}<field>{c}</field></columns>"
        for c, aggs in cols)
    sort = f"<sortColumn>{sort_by}</sortColumn><sortOrder>Desc</sortOrder>" if sort_by else ""
    aggs = "".join(
        f"<aggregates><calculatedFormula>{f}</calculatedFormula><datatype>number</datatype><developerName>{dev}</developerName>"
        f"<isActive>true</isActive><isCrossBlock>false</isCrossBlock><masterLabel>{lbl}</masterLabel><scale>1</scale></aggregates>"
        for dev, lbl, f in formulas)
    write(os.path.join(BASE, "reports", FOLDER, f"{name}.report-meta.xml"), f"""
<Report xmlns="http://soap.sforce.com/2006/04/metadata">
    {aggs}
    {columns}
    <description>{desc}</description>
    <filter>{''.join(crit(*c) for c in criteria)}</filter>
    <format>Summary</format>
    <groupingsDown><dateGranularity>Day</dateGranularity><field>{group}</field><sortOrder>Asc</sortOrder></groupingsDown>
    <name>{label}</name>
    <params><name>co</name><value>1</value></params>
    <reportType>{rtype}</reportType>
    <scope>{scope}</scope>
    <showDetails>true</showDetails>
    <showGrandTotal>true</showGrandTotal>
    <showSubTotals>true</showSubTotals>
    {sort}
    <timeFrameFilter><dateColumn>{date_col}</dateColumn><interval>INTERVAL_CUSTOM</interval></timeFrameFilter>
</Report>""")


HUNTER = [("Account.Hunter_Rank__c", "greaterThan", "0")]
report("Hunter_Operators_by_Unrealized_Spend", "Hunter: Top 10 Operators", "AccountList",
       [("Account.Unrealized_Annual_Spend__c", ["Sum"]), ("Account.Dark_Locations__c", ["Sum"]),
        ("Account.Location_Count__c", ["Sum"]), ("Account.Brands_Operated__c", [])],
       HUNTER + [("Account.Hunter_Rank__c", "lessOrEqual", "10")], "ACCOUNT.NAME",
       desc="Top 10 operators Hunter ranked by unrealized annual spend.")
report("Hunter_Book_Totals", "Hunter: Colorado Book Totals", "AccountList",
       [("Account.Unrealized_Annual_Spend__c", ["Sum"]), ("Account.Dark_Locations__c", ["Sum"]),
        ("Account.Paying_Locations__c", ["Sum"]), ("Account.Location_Count__c", ["Sum"])],
       HUNTER, "USERS.NAME", desc="Operators in the Colorado book, by owner.")
report("Location_Status", "Hunter: Paying vs Dark Locations", "AccountList",
       [("ACCOUNT.NAME", []), ("Account.Brand__c", [])],
       [("Account.Location_Status__c", "notEqual", "")], "Account.Location_Status__c",
       desc="Location accounts under Hunter-identified operators.")
report("Hunter_Pipeline_by_Stage", "Hunter: Multi-Location Pipeline by Stage", "Opportunity",
       [("AMOUNT", ["Sum"]), ("OPPORTUNITY_NAME", []), ("ACCOUNT_NAME", [])],
       [("OPPORTUNITY_NAME", "contains", "Multi-Location Activation")], "STAGE_NAME", date_col="CLOSE_DATE",
       desc="Opportunities Hunter opened for top operators.")
report("Piper_Multi_Location_Leads", "Piper: Multi-Location Leads Found", "LeadList",
       [("Lead.Unrealized_Annual_Spend__c", ["Sum"]), ("Lead.Location_Count__c", ["Sum"]), ("FIRST_NAME", []), ("LAST_NAME", []),
        ("COMPANY", []), ("Lead.Brands_Operated__c", [])],
       [("Lead.Multi_Location__c", "equals", "1")], "Lead.Agent_Source__c",
       desc="Inbound leads Piper qualified as multi-location.", scope="org")

QUOTA = 150000  # Tom's quarterly quota (matches scripts/demo_data.py TOM_QUARTERLY_QUOTA)
report("Tom_Pipeline_Coverage", "Tom: Colorado Pipeline Coverage", "Opportunity",
       [("AMOUNT", ["Sum"]), ("OPPORTUNITY_NAME", []), ("ACCOUNT_NAME", []), ("STAGE_NAME", [])],
       [("FULL_NAME", "equals", "Tom Jones"), ("CLOSED", "equals", "False"), ("OPPORTUNITY_NAME", "contains", "Multi-Location")], "TYPE", date_col="CLOSE_DATE",
       desc=f"Tom's open pipeline vs a ${QUOTA:,} quarterly quota. Add-On Business = existing; New Business = Hunter.",
       formulas=[("FORMULA1", "Pipeline Coverage (x quota)", f"AMOUNT:SUM/{QUOTA}")])

write(os.path.join(BASE, "reports", f"{FOLDER}.reportFolder-meta.xml"), f"""
<ReportFolder xmlns="http://soap.sforce.com/2006/04/metadata">
    <accessType>Public</accessType><name>Yelp Find and Win</name><publicFolderAccess>ReadWrite</publicFolderAccess>
</ReportFolder>""")
write(os.path.join(BASE, "dashboards", f"{FOLDER}_Dashboards.dashboardFolder-meta.xml"), f"""
<DashboardFolder xmlns="http://soap.sforce.com/2006/04/metadata">
    <accessType>Public</accessType><name>Yelp Find and Win Dashboards</name><publicFolderAccess>ReadWrite</publicFolderAccess>
</DashboardFolder>""")


def comp(ctype, rep, title, header, col, row, cs, rs, extra=""):
    return f"""
        <dashboardGridComponents>
            <colSpan>{cs}</colSpan><columnIndex>{col}</columnIndex>
            <dashboardComponent>
                <autoselectColumnsFromReport>false</autoselectColumnsFromReport>
                {extra}
                <componentType>{ctype}</componentType>
                <displayUnits>Auto</displayUnits>
                <groupingSortProperties/>
                <header>{header}</header>
                <report>{FOLDER}/{rep}</report>
                <showRange>false</showRange>
                <title>{title}</title>
            </dashboardComponent>
            <rowIndex>{row}</rowIndex><rowSpan>{rs}</rowSpan>
        </dashboardGridComponents>"""


CHART = "<chartAxisRange>Auto</chartAxisRange><enableHover>true</enableHover><legendPosition>Bottom</legendPosition><showPercentage>false</showPercentage><showValues>true</showValues><sortBy>RowValueDescending</sortBy><useReportChart>false</useReportChart>"
GREEN = ("<indicatorBreakpoint1>1.0</indicatorBreakpoint1><indicatorBreakpoint2>2.0</indicatorBreakpoint2>"
         "<indicatorHighColor>#04844B</indicatorHighColor><indicatorLowColor>#04844B</indicatorLowColor><indicatorMiddleColor>#04844B</indicatorMiddleColor>")  # metric tiles always green
INDICATORS = "<indicatorHighColor>#54C254</indicatorHighColor><indicatorLowColor>#C25454</indicatorLowColor><indicatorMiddleColor>#C2C254</indicatorMiddleColor>"
METRIC = "<chartSummary><aggregate>Sum</aggregate><axisBinding>y</axisBinding><column>{}</column></chartSummary>"
GAUGE = ("<chartSummary><axisBinding>y</axisBinding><column>FORMULA1</column></chartSummary>"
         "<gaugeMax>4.0</gaugeMax><gaugeMin>0.0</gaugeMin>"
         "<indicatorBreakpoint1>2.0</indicatorBreakpoint1><indicatorBreakpoint2>3.0</indicatorBreakpoint2>" + INDICATORS)
comps = "".join([
    comp("Metric", "Hunter_Book_Totals", "Net-new annual revenue in Tom's top 40", "Nina · CRO", 0, 0, 3, 4,
         METRIC.format("Account.Unrealized_Annual_Spend__c") + GREEN),
    comp("Metric", "Hunter_Book_Totals", "Dark locations owners already control", "Nina · CRO", 3, 0, 3, 4,
         METRIC.format("Account.Dark_Locations__c") + GREEN),
    comp("Metric", "Hunter_Pipeline_by_Stage", "Multi-location pipeline Hunter opened", "Marcus · Sales", 6, 0, 3, 4,
         METRIC.format("AMOUNT") + GREEN),
    comp("Metric", "Piper_Multi_Location_Leads", "Multi-location value Piper found", "Priya · Demand Gen", 9, 0, 3, 4,
         METRIC.format("Lead.Unrealized_Annual_Spend__c") + GREEN),
    comp("Gauge", "Tom_Pipeline_Coverage", "Coverage vs 3.0x target (was 2.1x)", "Marcus · Pipeline coverage", 0, 4, 4, 8, GAUGE),
    comp("Bar", "Hunter_Operators_by_Unrealized_Spend", "Top 10 operators by unrealized spend", "Marcus + Tom · Where to work", 4, 4, 5, 8,
         CHART + METRIC.format("Account.Unrealized_Annual_Spend__c") + "<groupingColumn>ACCOUNT.NAME</groupingColumn>"),
    comp("Donut", "Location_Status", "Paying vs dark locations", "Nina · Paid locations", 9, 4, 3, 8,
         CHART + "<chartSummary><axisBinding>y</axisBinding><column>RowCount</column></chartSummary><groupingColumn>Account.Location_Status__c</groupingColumn>"),
    comp("Column", "Hunter_Pipeline_by_Stage", "Hunter pipeline by stage", "Marcus · Hunter pipeline", 0, 12, 6, 8,
         CHART + METRIC.format("AMOUNT") + "<groupingColumn>STAGE_NAME</groupingColumn>"),
    comp("Donut", "Tom_Pipeline_Coverage", "Tom's pipeline: existing vs Hunter", "Marcus + Tom · Where coverage came from", 6, 12, 6, 8,
         CHART + METRIC.format("AMOUNT") + "<groupingColumn>TYPE</groupingColumn>"),
])
write(os.path.join(BASE, "dashboards", f"{FOLDER}_Dashboards", "Find_and_Win_Leadership.dashboard-meta.xml"), f"""
<Dashboard xmlns="http://soap.sforce.com/2006/04/metadata">
    <backgroundEndColor>#FFFFFF</backgroundEndColor>
    <backgroundFadeDirection>Diagonal</backgroundFadeDirection>
    <backgroundStartColor>#FFFFFF</backgroundStartColor>
    <chartTheme>light</chartTheme>
    <colorPalette>unity</colorPalette>
    <dashboardChartTheme>light</dashboardChartTheme>
    <dashboardColorPalette>unity</dashboardColorPalette>
    <dashboardGridLayout>{comps}
        <numberOfColumns>12</numberOfColumns>
        <rowHeight>36</rowHeight>
    </dashboardGridLayout>
    <dashboardType>SpecifiedUser</dashboardType>
    <description>Find and Win: what Piper and Hunter put in the CRM, one view per leader.</description>
    <isGridLayout>true</isGridLayout>
    <runningUser>{RUNNING_USER}</runningUser>
    <textColor>#000000</textColor>
    <title>Yelp Find and Win: Leadership View</title>
    <titleColor>#000000</titleColor>
    <titleSize>12</titleSize>
</Dashboard>""")
print("ok")
