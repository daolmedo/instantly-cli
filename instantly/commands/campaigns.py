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


@campaigns_app.command("list")
def list_campaigns(
    limit: int = typer.Option(10, help="Number of campaigns to return", min=1, max=100),
    search: Optional[str] = typer.Option(None, help="Filter by campaign name"),
    status: Optional[int] = typer.Option(None, help="Filter by campaign status (0, 1, 2, 3)", min=0, max=3),
    starting_after: Optional[str] = typer.Option(None, help="Pagination cursor"),
):
    """List campaigns."""
    params = {
        "limit": limit,
    }
    if search is not None:
        params["search"] = search
    if status is not None:
        params["status"] = status
    if starting_after is not None:
        params["starting_after"] = starting_after

    client = InstantlyClient()
    result = client.get("/api/v2/campaigns", params=params)
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
