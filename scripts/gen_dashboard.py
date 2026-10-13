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


def report(name, label, rtype, cols, criteria, group, sort_by=None, date_col="CREATED_DATE", desc="", scope="organization", formulas=(), granularity="Day", params=()):
    columns = "".join(
        f"<columns>{''.join(f'<aggregateTypes>{a}</aggregateTypes>' for a in aggs)}<field>{c}</field></columns>"
        for c, aggs in cols)
    sort = f"<sortColumn>{sort_by}</sortColumn><sortOrder>Desc</sortOrder>" if sort_by else ""
    extra_params = "".join(f"<params><name>{k}</name><value>{v}</value></params>" for k, v in params)
    timeframe = (f"<timeFrameFilter><dateColumn>{date_col}</dateColumn><interval>INTERVAL_CUSTOM</interval></timeFrameFilter>"
                 if date_col else "")
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
    <groupingsDown><dateGranularity>{granularity}</dateGranularity><field>{group}</field><sortOrder>Asc</sortOrder></groupingsDown>
    <name>{label}</name>
    <params><name>co</name><value>1</value></params>{extra_params}
    <reportType>{rtype}</reportType>
    <scope>{scope}</scope>
    <showDetails>true</showDetails>
    <showGrandTotal>true</showGrandTotal>
    <showSubTotals>true</showSubTotals>
    {sort}
    {timeframe}
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


# --- Nina's "is agentic AI working?" reports ---
MULTI = [("OPPORTUNITY_NAME", "contains", "Multi-Location"), ("CLOSED", "equals", "False")]
report("Pipeline_by_Agent_Source", "Pipeline by Source (Piper, Hunter, Rep)", "Opportunity",
       [("AMOUNT", ["Sum"]), ("OPPORTUNITY_NAME", []), ("ACCOUNT_NAME", [])],
       MULTI, "Opportunity.Agent_Source__c", date_col="CLOSE_DATE", desc="Open multi-location pipeline by where it came from.")
report("Piper_Sourced_Pipeline", "Piper: Sourced Pipeline", "Opportunity",
       [("AMOUNT", ["Sum"]), ("OPPORTUNITY_NAME", []), ("ACCOUNT_NAME", [])],
       MULTI + [("Opportunity.Agent_Source__c", "equals", "Piper")], "STAGE_NAME", date_col="CLOSE_DATE",
       desc="Pipeline from inbound owners Piper qualified.")
report("Hunter_Account_Plans", "Hunter: Account Plans Built", "Activity",
       [("SUBJECT", []), ("STATUS", [])],
       [("SUBJECT", "startsWith", "Hunter brief"), ("TASK", "equals", "True")], "ASSIGNED", date_col="DUE_DATE",
       desc="Operator briefs (account plans) Hunter wrote for reps.")
report("Hunter_Outreach_Results", "Hunter: Outreach Results", "CampaignWithCampaignMembers",
       [("MEMBER_TYPE", [])], [("CAMPAIGN_NAME", "equals", "Hunter - Colorado Dark Location Outreach")],
       "MEMBER_STATUS", date_col=None, desc="Owner responses to Hunter's outreach.")
report("Hunter_Outreach_Replies", "Hunter: Owners Who Replied", "CampaignWithCampaignMembers",
       [("MEMBER_TYPE", [])], [("CAMPAIGN_NAME", "equals", "Hunter - Colorado Dark Location Outreach"),
                               ("HAS_RESPONDED", "equals", "True")],
       "MEMBER_STATUS", date_col=None, desc="Owners who replied to or booked from Hunter outreach.")
report("Data_Hygiene_by_Source", "Data Hygiene: Field Completeness", "Opportunity",
       [("Opportunity.Field_Completeness__c", ["Average"]), ("OPPORTUNITY_NAME", [])],
       MULTI, "Opportunity.Agent_Source__c", date_col="CLOSE_DATE",
       desc="Average field completeness: agent-created vs rep-entered opportunities.")
report("Customer_Meetings_per_Week", "Customer Meetings per Week", "Activity",
       [("SUBJECT", []), ("ASSIGNED", [])],
       [("SUBJECT", "startsWith", "Yelp customer meeting")], "DUE_DATE", date_col="DUE_DATE",
       desc="Customer meetings held by the Colorado team, by week.", granularity="Week",
       params=[("closed", "all"), ("type", "e")])

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
ROWS = "<chartSummary><axisBinding>y</axisBinding><column>RowCount</column></chartSummary>"
comps = "".join([
    # 1 · Find: what Piper and Hunter uncovered
    comp("Metric", "Piper_Sourced_Pipeline", "Pipeline sourced by Piper", "1 · Find", 0, 0, 3, 4,
         METRIC.format("AMOUNT") + GREEN),
    comp("Metric", "Hunter_Book_Totals", "Dark locations Hunter uncovered", "1 · Find", 3, 0, 3, 4,
         METRIC.format("Account.Dark_Locations__c") + GREEN),
    # 2 · Plan and outreach
    comp("Metric", "Hunter_Account_Plans", "Account plans built by Hunter", "2 · Account planning", 6, 0, 3, 4,
         ROWS + GREEN),
    comp("Metric", "Hunter_Outreach_Replies", "Owners who replied to outreach", "2 · Outreach", 9, 0, 3, 4,
         ROWS + GREEN),
    # Pipeline: the headline
    comp("Gauge", "Tom_Pipeline_Coverage", "Coverage vs 3.0x target (was 2.1x)", "Pipeline coverage", 0, 4, 4, 8, GAUGE),
    comp("Donut", "Pipeline_by_Agent_Source", "Where the pipeline came from", "Pipeline by source", 4, 4, 4, 8,
         CHART + METRIC.format("AMOUNT") + "<groupingColumn>Opportunity.Agent_Source__c</groupingColumn>"),
    comp("Bar", "Hunter_Outreach_Results", "Hunter outreach: 40 owners contacted", "2 · Outreach effectiveness", 8, 4, 4, 8,
         CHART + ROWS + "<groupingColumn>MEMBER_STATUS</groupingColumn>"),
    # 3 · Data hygiene and 4 · Meetings
    comp("Bar", "Data_Hygiene_by_Source", "Field completeness: agents vs reps", "3 · Data hygiene", 0, 12, 6, 8,
         CHART + "<chartSummary><aggregate>Average</aggregate><axisBinding>y</axisBinding><column>Opportunity.Field_Completeness__c</column></chartSummary>"
         "<groupingColumn>Opportunity.Agent_Source__c</groupingColumn>"),
    comp("Column", "Customer_Meetings_per_Week", "Customer meetings per week", "4 · Customer meetings", 6, 12, 6, 8,
         CHART.replace("<sortBy>RowValueDescending</sortBy>", "<sortBy>RowLabelAscending</sortBy>") + ROWS + "<groupingColumn>DUE_DATE</groupingColumn>"),
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
    <description>Nina's view: pipeline, outreach, data hygiene and meetings since Piper and Hunter went live.</description>
    <isGridLayout>true</isGridLayout>
    <runningUser>{RUNNING_USER}</runningUser>
    <textColor>#000000</textColor>
    <title>Is Agentic AI Working? Find and Win (Colorado)</title>
    <titleColor>#000000</titleColor>
    <titleSize>12</titleSize>
</Dashboard>""")
print("ok")
