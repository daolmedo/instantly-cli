import json
from typing import Optional

import typer

from instantly.client import InstantlyClient

leads_app = typer.Typer(no_args_is_help=True)


@leads_app.command()
def create(
    email: Optional[str] = typer.Option(None, help="Email address of the lead"),
    first_name: Optional[str] = typer.Option(None, help="First name"),
    last_name: Optional[str] = typer.Option(None, help="Last name"),
    campaign: Optional[str] = typer.Option(None, help="Campaign UUID"),
    list_id: Optional[str] = typer.Option(None, help="List UUID"),
    company_name: Optional[str] = typer.Option(None, help="Company name"),
    phone: Optional[str] = typer.Option(None, help="Phone number"),
    website: Optional[str] = typer.Option(None, help="Website URL"),
    personalization: Optional[str] = typer.Option(None, help="Personalization text"),
    lt_interest_status: Optional[int] = typer.Option(None, help="Interest status (e.g. 1=Interested, -1=Not Interested)"),
    pl_value_lead: Optional[str] = typer.Option(None, help="Potential value of the lead"),
    assigned_to: Optional[str] = typer.Option(None, help="Assigned user UUID"),
    skip_if_in_workspace: Optional[bool] = typer.Option(None, help="Skip if lead already in workspace"),
    skip_if_in_campaign: Optional[bool] = typer.Option(None, help="Skip if lead already in campaign"),
    skip_if_in_list: Optional[bool] = typer.Option(None, help="Skip if lead already in list"),
    blocklist_id: Optional[str] = typer.Option(None, help="Blocklist UUID to check"),
    verify_leads_for_lead_finder: Optional[bool] = typer.Option(None, help="Verify leads for lead finder"),
    verify_leads_on_import: Optional[bool] = typer.Option(None, help="Verify leads on import"),
    custom_variables: Optional[str] = typer.Option(None, help="Custom variables as JSON string"),
):
    """Create a new lead."""
    payload: dict = {}
    if campaign is not None:
        payload["campaign"] = campaign
    if email is not None:
        payload["email"] = email
    if first_name is not None:
        payload["first_name"] = first_name
    if last_name is not None:
        payload["last_name"] = last_name
    if company_name is not None:
        payload["company_name"] = company_name
    if phone is not None:
        payload["phone"] = phone
    if website is not None:
        payload["website"] = website
    if personalization is not None:
        payload["personalization"] = personalization
    if lt_interest_status is not None:
        payload["lt_interest_status"] = lt_interest_status
    if pl_value_lead is not None:
        payload["pl_value_lead"] = pl_value_lead
    if list_id is not None:
        payload["list_id"] = list_id
    if assigned_to is not None:
        payload["assigned_to"] = assigned_to
    if skip_if_in_workspace is not None:
        payload["skip_if_in_workspace"] = skip_if_in_workspace
    if skip_if_in_campaign is not None:
        payload["skip_if_in_campaign"] = skip_if_in_campaign
    if skip_if_in_list is not None:
        payload["skip_if_in_list"] = skip_if_in_list
    if blocklist_id is not None:
        payload["blocklist_id"] = blocklist_id
    if verify_leads_for_lead_finder is not None:
        payload["verify_leads_for_lead_finder"] = verify_leads_for_lead_finder
    if verify_leads_on_import is not None:
        payload["verify_leads_on_import"] = verify_leads_on_import
    if custom_variables is not None:
        payload["custom_variables"] = json.loads(custom_variables)

    client = InstantlyClient()
    result = client.post("/api/v2/leads", json=payload)
    print(json.dumps(result, indent=2))


@leads_app.command()
def get(
    id: str = typer.Argument(help="UUID of the lead to retrieve"),
):
    """Get a single lead by ID."""
    client = InstantlyClient()
    result = client.get(f"/api/v2/leads/{id}")
    print(json.dumps(result, indent=2))


@leads_app.command("list")
def list_leads(
    search: Optional[str] = typer.Option(None, help="Search by first name, last name, or email"),
    filter: Optional[str] = typer.Option(None, help="Filter enum (e.g. FILTER_VAL_CONTACTED, FILTER_LEAD_INTERESTED)"),
    campaign: Optional[str] = typer.Option(None, help="Campaign UUID to filter by"),
    list_id: Optional[str] = typer.Option(None, help="List UUID to filter by"),
    in_campaign: Optional[bool] = typer.Option(None, help="Whether the lead is in a campaign"),
    in_list: Optional[bool] = typer.Option(None, help="Whether the lead is in a list"),
    ids: Optional[str] = typer.Option(None, help="Comma-separated lead UUIDs to include"),
    excluded_ids: Optional[str] = typer.Option(None, help="Comma-separated lead UUIDs to exclude"),
    contacts: Optional[str] = typer.Option(None, help="Comma-separated email addresses the leads must have"),
    limit: Optional[int] = typer.Option(None, help="Number of items to return (1-100)"),
    starting_after: Optional[str] = typer.Option(None, help="Pagination cursor (lead ID or email when distinct_contacts is true)"),
    organization_user_ids: Optional[str] = typer.Option(None, help="Comma-separated organization user UUIDs"),
    smart_view_id: Optional[str] = typer.Option(None, help="Smart view UUID to filter by"),
    is_website_visitor: Optional[bool] = typer.Option(None, help="Whether the lead is a website visitor"),
    distinct_contacts: Optional[bool] = typer.Option(None, help="Whether to return distinct contacts"),
    enrichment_status: Optional[int] = typer.Option(None, help="Enrichment status (1=Enriched, 11=Pending, -1=N/A, -2=Error)"),
    esg_code: Optional[str] = typer.Option(None, help="ESG code (0=In Queue, 1=Barracuda, 2=Mimecast, etc.)"),
    queries: Optional[str] = typer.Option(None, help="Query filters as JSON array string"),
    assigned_to: Optional[str] = typer.Option(None, help="Assigned user UUID"),
):
    """List leads. Note: this is a POST endpoint due to complex filtering."""
    payload: dict = {}
    if search is not None:
        payload["search"] = search
    if filter is not None:
        payload["filter"] = filter
    if campaign is not None:
        payload["campaign"] = campaign
    if list_id is not None:
        payload["list_id"] = list_id
    if in_campaign is not None:
        payload["in_campaign"] = in_campaign
    if in_list is not None:
        payload["in_list"] = in_list
    if ids is not None:
        payload["ids"] = [s.strip() for s in ids.split(",")]
    if excluded_ids is not None:
        payload["excluded_ids"] = [s.strip() for s in excluded_ids.split(",")]
    if contacts is not None:
        payload["contacts"] = [s.strip() for s in contacts.split(",")]
    if limit is not None:
        payload["limit"] = limit
    if starting_after is not None:
        payload["starting_after"] = starting_after
    if organization_user_ids is not None:
        payload["organization_user_ids"] = [s.strip() for s in organization_user_ids.split(",")]
    if smart_view_id is not None:
        payload["smart_view_id"] = smart_view_id
    if is_website_visitor is not None:
        payload["is_website_visitor"] = is_website_visitor
    if distinct_contacts is not None:
        payload["distinct_contacts"] = distinct_contacts
    if enrichment_status is not None:
        payload["enrichment_status"] = enrichment_status
    if esg_code is not None:
        payload["esg_code"] = esg_code
    if queries is not None:
        payload["queries"] = json.loads(queries)
    if assigned_to is not None:
        payload["assigned_to"] = assigned_to

    client = InstantlyClient()
    result = client.post("/api/v2/leads/list", json=payload)
    print(json.dumps(result, indent=2))


@leads_app.command()
def update(
    id: str = typer.Argument(help="UUID of the lead to update"),
    first_name: Optional[str] = typer.Option(None, help="First name"),
    last_name: Optional[str] = typer.Option(None, help="Last name"),
    company_name: Optional[str] = typer.Option(None, help="Company name"),
    phone: Optional[str] = typer.Option(None, help="Phone number"),
    website: Optional[str] = typer.Option(None, help="Website URL"),
    personalization: Optional[str] = typer.Option(None, help="Personalization text"),
    lt_interest_status: Optional[int] = typer.Option(None, help="Interest status (e.g. 1=Interested, -1=Not Interested)"),
    pl_value_lead: Optional[str] = typer.Option(None, help="Potential value of the lead"),
    assigned_to: Optional[str] = typer.Option(None, help="Assigned user UUID"),
    custom_variables: Optional[str] = typer.Option(None, help="Custom variables as JSON string"),
):
    """Update an existing lead."""
    payload: dict = {}
    if first_name is not None:
        payload["first_name"] = first_name
    if last_name is not None:
        payload["last_name"] = last_name
    if company_name is not None:
        payload["company_name"] = company_name
    if phone is not None:
        payload["phone"] = phone
    if website is not None:
        payload["website"] = website
    if personalization is not None:
        payload["personalization"] = personalization
    if lt_interest_status is not None:
        payload["lt_interest_status"] = lt_interest_status
    if pl_value_lead is not None:
        payload["pl_value_lead"] = pl_value_lead
    if assigned_to is not None:
        payload["assigned_to"] = assigned_to
    if custom_variables is not None:
        payload["custom_variables"] = json.loads(custom_variables)

    if not payload:
        print("Error: at least one field to update is required.")
        raise typer.Exit(code=1)

    client = InstantlyClient()
    result = client.patch(f"/api/v2/leads/{id}", json=payload)
    print(json.dumps(result, indent=2))


@leads_app.command("update-interest")
def update_interest(
    lead_email: str = typer.Option(..., help="Email of the lead to update"),
    interest_value: Optional[int] = typer.Option(None, help="Interest status value (null resets to 'Lead')"),
    reset_interest: bool = typer.Option(False, help="Reset interest to null (moves lead to 'Lead' status)"),
    campaign_id: Optional[str] = typer.Option(None, help="Campaign UUID"),
    ai_interest_value: Optional[int] = typer.Option(None, help="AI interest value"),
    disable_auto_interest: Optional[bool] = typer.Option(None, help="Disable auto interest"),
    list_id: Optional[str] = typer.Option(None, help="List UUID"),
):
    """Update the interest status of a lead."""
    payload: dict = {
        "lead_email": lead_email,
    }
    if reset_interest:
        payload["interest_value"] = None
    elif interest_value is not None:
        payload["interest_value"] = interest_value
    else:
        print("Error: provide --interest-value or --reset-interest.")
        raise typer.Exit(code=1)

    if campaign_id is not None:
        payload["campaign_id"] = campaign_id
    if ai_interest_value is not None:
        payload["ai_interest_value"] = ai_interest_value
    if disable_auto_interest is not None:
        payload["disable_auto_interest"] = disable_auto_interest
    if list_id is not None:
        payload["list_id"] = list_id

    client = InstantlyClient()
    result = client.post("/api/v2/leads/update-interest-status", json=payload)
    print(json.dumps(result, indent=2))
