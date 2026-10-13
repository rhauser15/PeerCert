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


def report(name, label, rtype, cols, criteria, group, sort_by=None, date_col="CREATED_DATE", desc="", scope="organization"):
    columns = "".join(
        f"<columns>{''.join(f'<aggregateTypes>{a}</aggregateTypes>' for a in aggs)}<field>{c}</field></columns>"
        for c, aggs in cols)
    sort = f"<sortColumn>{sort_by}</sortColumn><sortOrder>Desc</sortOrder>" if sort_by else ""
    write(os.path.join(BASE, "reports", FOLDER, f"{name}.report-meta.xml"), f"""
<Report xmlns="http://soap.sforce.com/2006/04/metadata">
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
INDICATORS = "<indicatorHighColor>#54C254</indicatorHighColor><indicatorLowColor>#C25454</indicatorLowColor><indicatorMiddleColor>#C2C254</indicatorMiddleColor>"
METRIC = "<chartSummary><aggregate>Sum</aggregate><axisBinding>y</axisBinding><column>{}</column></chartSummary>"
comps = "".join([
    comp("Metric", "Hunter_Book_Totals", "Net-new annual revenue in Tom's top 40", "Nina · CRO", 0, 0, 3, 4,
         METRIC.format("Account.Unrealized_Annual_Spend__c") + INDICATORS),
    comp("Metric", "Hunter_Book_Totals", "Dark locations owners already control", "Nina · CRO", 3, 0, 3, 4,
         METRIC.format("Account.Dark_Locations__c") + INDICATORS),
    comp("Metric", "Hunter_Pipeline_by_Stage", "Multi-location pipeline Hunter opened", "Marcus · Sales", 6, 0, 3, 4,
         METRIC.format("AMOUNT") + INDICATORS),
    comp("Metric", "Piper_Multi_Location_Leads", "Multi-location value Piper found", "Priya · Demand Gen", 9, 0, 3, 4,
         METRIC.format("Lead.Unrealized_Annual_Spend__c") + INDICATORS),
    comp("Bar", "Hunter_Operators_by_Unrealized_Spend", "Top 10 operators by unrealized spend", "Marcus + Tom · Where to work", 0, 4, 6, 8,
         CHART + METRIC.format("Account.Unrealized_Annual_Spend__c") + "<groupingColumn>ACCOUNT.NAME</groupingColumn>"),
    comp("Donut", "Location_Status", "Paying vs dark locations", "Nina · Paid locations", 6, 4, 3, 8,
         CHART + "<chartSummary><axisBinding>y</axisBinding><column>RowCount</column></chartSummary><groupingColumn>Account.Location_Status__c</groupingColumn>"),
    comp("Column", "Hunter_Pipeline_by_Stage", "Hunter pipeline by stage", "Marcus · Coverage", 9, 4, 3, 8,
         CHART + METRIC.format("AMOUNT") + "<groupingColumn>STAGE_NAME</groupingColumn>"),
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
