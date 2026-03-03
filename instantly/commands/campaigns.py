import json
import sys
from pathlib import Path
from typing import Optional

import typer

from instantly.client import InstantlyClient

campaigns_app = typer.Typer(no_args_is_help=True)

SUPPORTED_CSV_LEAD_FIELDS = {
    "email",
    "first_name",
    "last_name",
    "company_name",
    "phone",
    "website",
    "personalization",
}


def _parse_json_leads(raw: str, source_label: str) -> list:
    leads = json.loads(raw)
    if not isinstance(leads, list):
        print(f"Error: {source_label} must contain a JSON array of lead objects.")
        raise typer.Exit(code=1)
    return leads


def _parse_csv_leads(raw: str) -> list:
    lines = [line.strip() for line in raw.split("\n")]
    lines = [line for line in lines if line]
    if not lines:
        return []

    headers = [header.strip().rstrip("\r") for header in lines[0].split(",")]
    leads = []
    for line in lines[1:]:
        values = [value.strip().rstrip("\r") for value in line.split(",")]
        lead = {}
        for idx, header in enumerate(headers):
            if header not in SUPPORTED_CSV_LEAD_FIELDS:
                continue
            lead[header] = values[idx] if idx < len(values) else ""
        leads.append(lead)
    return leads


def _load_leads_input(file: Optional[str]) -> list:
    if not file:
        if sys.stdin.isatty():
            print("Error: provide --file (.json or .csv), or pipe a JSON array through stdin.")
            raise typer.Exit(code=1)
        return _parse_json_leads(sys.stdin.read(), "stdin")

    raw = Path(file).read_text(encoding="utf-8")
    normalized_path = str(file).lower()
    if normalized_path.endswith(".csv"):
        return _parse_csv_leads(raw)
    if normalized_path.endswith(".json"):
        return _parse_json_leads(raw, "file")

    print("Error: file extension must be .json or .csv.")
    raise typer.Exit(code=1)


STATUS_LABELS = {
    0: "Draft",
    1: "Active",
    2: "Paused",
    3: "Completed",
    4: "Running Subsequences",
    -1: "Accounts Unhealthy",
    -2: "Bounce Protect",
    -99: "Account Suspended",
}


@campaigns_app.command("list")
def list_campaigns(
    limit: int = typer.Option(10, help="Number of campaigns to return", min=1, max=100),
    search: Optional[str] = typer.Option(None, help="Filter by campaign name"),
    status: Optional[int] = typer.Option(None, help="Filter by campaign status (0, 1, 2, 3)", min=0, max=3),
    starting_after: Optional[str] = typer.Option(None, help="Pagination cursor"),
    sort: str = typer.Option("newest", help="Sort order: newest or oldest (by timestamp_created)"),
    brief: bool = typer.Option(False, "--brief", help="Token-efficient output: id, name, status, created"),
):
    """List campaigns, sorted newest-first by default."""
    params = {"limit": limit}
    if search is not None:
        params["search"] = search
    if status is not None:
        params["status"] = status
    if starting_after is not None:
        params["starting_after"] = starting_after

    client = InstantlyClient()

    # Fetch all campaigns across pages so sorting is global, not per-page
    all_items = []
    fetch_params = {k: v for k, v in params.items() if k != "limit"}
    fetch_params["limit"] = 100
    next_cursor = params.get("starting_after")
    while True:
        if next_cursor:
            fetch_params["starting_after"] = next_cursor
        page = client.get("/api/v2/campaigns", params=fetch_params)
        items = page.get("items", [])
        all_items.extend(items)
        next_cursor = page.get("next_starting_after")
        if not next_cursor or len(items) < 100:
            break

    reverse = sort != "oldest"
    all_items = sorted(all_items, key=lambda c: c.get("timestamp_created", ""), reverse=reverse)
    result = {"items": all_items[:limit]}

    if brief:
        items = [
            {
                "id": c["id"],
                "name": c["name"],
                "status": STATUS_LABELS.get(c.get("status"), c.get("status")),
                "created": c.get("timestamp_created", ""),
            }
            for c in result.get("items", [])
        ]
        print(json.dumps(items))
    else:
        print(json.dumps(result, indent=2))


@campaigns_app.command()
def get(
    id: str = typer.Argument(help="UUID of the campaign to retrieve"),
):
    """Get a single campaign by ID."""
    client = InstantlyClient()
    result = client.get(f"/api/v2/campaigns/{id}")
    print(json.dumps(result, indent=2))


@campaigns_app.command()
def activate(
    id: str = typer.Argument(help="UUID of the campaign to activate"),
):
    """Activate a campaign."""
    client = InstantlyClient()
    result = client.post(f"/api/v2/campaigns/{id}/activate")
    print(json.dumps(result, indent=2))


@campaigns_app.command()
def pause(
    id: str = typer.Argument(help="UUID of the campaign to pause"),
):
    """Pause a campaign."""
    client = InstantlyClient()
    result = client.post(f"/api/v2/campaigns/{id}/pause")
    print(json.dumps(result, indent=2))


@campaigns_app.command()
def duplicate(
    id: str = typer.Argument(help="UUID of the campaign to duplicate"),
    name: Optional[str] = typer.Option(None, help="Name for the duplicated campaign"),
):
    """Duplicate a campaign."""
    payload = {"name": name} if name else None
    client = InstantlyClient()
    result = client.post(f"/api/v2/campaigns/{id}/duplicate", json=payload)
    print(json.dumps(result, indent=2))


@campaigns_app.command()
def update(
    id: str = typer.Argument(help="UUID of the campaign to update"),
    name: Optional[str] = typer.Option(None, "--name", help="Campaign name"),
    daily_limit: Optional[int] = typer.Option(None, "--daily-limit", help="Daily email sending limit"),
    email_gap: Optional[int] = typer.Option(None, "--email-gap", help="Gap between emails in minutes"),
    random_wait_max: Optional[int] = typer.Option(None, "--random-wait-max", help="Max random wait in minutes"),
    stop_on_reply: Optional[bool] = typer.Option(
        None,
        "--stop-on-reply/--no-stop-on-reply",
        help="Whether to stop the campaign on reply",
    ),
    stop_on_auto_reply: Optional[bool] = typer.Option(
        None,
        "--stop-on-auto-reply/--no-stop-on-auto-reply",
        help="Whether to stop the campaign on auto-reply",
    ),
    link_tracking: Optional[bool] = typer.Option(
        None,
        "--link-tracking/--no-link-tracking",
        help="Whether link tracking is enabled",
    ),
    open_tracking: Optional[bool] = typer.Option(
        None,
        "--open-tracking/--no-open-tracking",
        help="Whether open tracking is enabled",
    ),
    daily_max_leads: Optional[int] = typer.Option(None, "--daily-max-leads", help="Max new leads per day"),
    text_only: Optional[bool] = typer.Option(
        None,
        "--text-only/--no-text-only",
        help="Whether emails should be sent as text-only",
    ),
    sequences: Optional[str] = typer.Option(None, "--sequences", help="Full sequences JSON string"),
):
    """Update a campaign."""
    payload = {}

    if name is not None:
        payload["name"] = name
    if daily_limit is not None:
        payload["daily_limit"] = daily_limit
    if email_gap is not None:
        payload["email_gap"] = email_gap
    if random_wait_max is not None:
        payload["random_wait_max"] = random_wait_max
    if stop_on_reply is not None:
        payload["stop_on_reply"] = stop_on_reply
    if stop_on_auto_reply is not None:
        payload["stop_on_auto_reply"] = stop_on_auto_reply
    if link_tracking is not None:
        payload["link_tracking"] = link_tracking
    if open_tracking is not None:
        payload["open_tracking"] = open_tracking
    if daily_max_leads is not None:
        payload["daily_max_leads"] = daily_max_leads
    if text_only is not None:
        payload["text_only"] = text_only
    if sequences is not None:
        try:
            payload["sequences"] = json.loads(sequences)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON for --sequences ({exc})")
            raise typer.Exit(code=1)

    if not payload:
        print("Error: provide at least one field to update.")
        raise typer.Exit(code=1)

    client = InstantlyClient()
    result = client.patch(f"/api/v2/campaigns/{id}", json=payload)
    print(json.dumps(result, indent=2))


@campaigns_app.command("add-leads")
def add_leads(
    campaign_id: str = typer.Argument(help="UUID of the campaign to add leads to"),
    file: Optional[str] = typer.Option(
        None,
        help="Path to a JSON or CSV file with leads; if omitted, reads JSON array from stdin",
    ),
    verify: bool = typer.Option(False, help="Verify leads on import"),
    skip_workspace: bool = typer.Option(False, help="Skip leads already in workspace"),
    skip_campaign: bool = typer.Option(False, help="Skip leads already in any campaign"),
    skip_list: bool = typer.Option(False, help="Skip leads already in any list"),
):
    """Add leads to a campaign."""
    try:
        leads = _load_leads_input(file)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON input ({exc})")
        raise typer.Exit(code=1)

    payload = {
        "campaign_id": campaign_id,
        "leads": leads,
        "verify_leads_on_import": verify,
        "skip_if_in_workspace": skip_workspace,
        "skip_if_in_campaign": skip_campaign,
        "skip_if_in_list": skip_list,
    }

    client = InstantlyClient()
    result = client.post("/api/v2/leads/add", json=payload)
    print(json.dumps(result, indent=2))
