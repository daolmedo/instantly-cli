import json
from pathlib import Path
from typing import Optional

import typer

from instantly.client import InstantlyClient


def _resolve_body(body_text, body_html, body_text_file, body_html_file):
    """Read body from flags or files. Files take precedence."""
    text = Path(body_text_file).read_text(encoding="utf-8") if body_text_file else body_text
    html = Path(body_html_file).read_text(encoding="utf-8") if body_html_file else body_html
    if not text and not html:
        print("Error: at least one of --body-text, --body-html, --body-text-file, or --body-html-file is required.")
        raise typer.Exit(code=1)
    body = {}
    if text:
        body["text"] = text
    if html:
        body["html"] = html
    return body

emails_app = typer.Typer(no_args_is_help=True)


@emails_app.command()
def forward(
    reply_to_uuid: str = typer.Option(..., help="ID of the email being forwarded"),
    to: str = typer.Option(..., help="Comma-separated list of recipient emails"),
    eaccount: str = typer.Option(..., help="Connected sender account in your workspace"),
    subject: str = typer.Option(..., help="Email subject"),
    body_text: Optional[str] = typer.Option(None, help="Plain-text body"),
    body_html: Optional[str] = typer.Option(None, help="HTML body"),
    body_text_file: Optional[str] = typer.Option(None, help="Read plain-text body from file"),
    body_html_file: Optional[str] = typer.Option(None, help="Read HTML body from file"),
    cc: Optional[str] = typer.Option(None, help="Comma-separated CC addresses"),
    bcc: Optional[str] = typer.Option(None, help="Comma-separated BCC addresses"),
    assigned_to: Optional[str] = typer.Option(None, help="UUID of assigned user"),
):
    """Forward an existing email to another recipient."""
    body = _resolve_body(body_text, body_html, body_text_file, body_html_file)

    payload: dict = {
        "reply_to_uuid": reply_to_uuid,
        "to_address_email_list": to,
        "eaccount": eaccount,
        "subject": subject,
        "body": body,
    }
    if cc:
        payload["cc_address_email_list"] = cc
    if bcc:
        payload["bcc_address_email_list"] = bcc
    if assigned_to:
        payload["assigned_to"] = assigned_to

    client = InstantlyClient()
    client.post("/api/v2/emails/forward", json=payload)
    print(json.dumps({"success": True}))


@emails_app.command()
def reply(
    reply_to_uuid: str = typer.Option(..., help="ID of the email to reply to"),
    eaccount: str = typer.Option(..., help="Connected sender account in your workspace"),
    subject: str = typer.Option(..., help="Email subject"),
    body_text: Optional[str] = typer.Option(None, help="Plain-text body"),
    body_html: Optional[str] = typer.Option(None, help="HTML body"),
    body_text_file: Optional[str] = typer.Option(None, help="Read plain-text body from file"),
    body_html_file: Optional[str] = typer.Option(None, help="Read HTML body from file"),
    cc: Optional[str] = typer.Option(None, help="Comma-separated CC addresses"),
    bcc: Optional[str] = typer.Option(None, help="Comma-separated BCC addresses"),
    reminder_ts: Optional[str] = typer.Option(None, help="Reminder timestamp (ISO 8601 datetime)"),
    assigned_to: Optional[str] = typer.Option(None, help="UUID of assigned user"),
):
    """Reply to an existing email."""
    body = _resolve_body(body_text, body_html, body_text_file, body_html_file)

    payload: dict = {
        "reply_to_uuid": reply_to_uuid,
        "eaccount": eaccount,
        "subject": subject,
        "body": body,
    }
    if cc:
        payload["cc_address_email_list"] = cc
    if bcc:
        payload["bcc_address_email_list"] = bcc
    if reminder_ts:
        payload["reminder_ts"] = reminder_ts
    if assigned_to:
        payload["assigned_to"] = assigned_to

    client = InstantlyClient()
    client.post("/api/v2/emails/reply", json=payload)
    print(json.dumps({"success": True}))


@emails_app.command("list")
def list_emails(
    limit: Optional[int] = typer.Option(None, help="Number of items to return (1-100)"),
    starting_after: Optional[str] = typer.Option(None, help="ID of last item from previous page (pagination)"),
    search: Optional[str] = typer.Option(None, help="Search by email address or 'thread:<thread_id>'"),
    campaign_id: Optional[str] = typer.Option(None, help="Filter by campaign UUID"),
    list_id: Optional[str] = typer.Option(None, help="Filter by lead list UUID"),
    i_status: Optional[int] = typer.Option(None, help="Filter by interest status"),
    eaccount: Optional[str] = typer.Option(None, help="Filter by sender account (comma-separated for multiple)"),
    is_unread: Optional[bool] = typer.Option(None, help="Filter by unread status"),
    has_reminder: Optional[bool] = typer.Option(None, help="Filter by reminder presence"),
    mode: Optional[str] = typer.Option(None, help="Filter mode: emode_focused, emode_others, emode_all"),
    preview_only: Optional[bool] = typer.Option(None, help="Only return email previews"),
    sort_order: Optional[str] = typer.Option(None, help="Sort order: asc or desc (default: desc)"),
    scheduled_only: Optional[bool] = typer.Option(None, help="Only return scheduled emails"),
    assigned_to: Optional[str] = typer.Option(None, help="Filter by assigned user UUID"),
    lead: Optional[str] = typer.Option(None, help="Filter by lead email address"),
    company_domain: Optional[str] = typer.Option(None, help="Filter by company domain"),
    marked_as_done: Optional[bool] = typer.Option(None, help="Filter by marked-as-done status"),
    email_type: Optional[str] = typer.Option(None, help="Filter by type: received, sent, manual"),
    min_timestamp_created: Optional[str] = typer.Option(None, help="Filter emails created after this ISO timestamp"),
    max_timestamp_created: Optional[str] = typer.Option(None, help="Filter emails created before this ISO timestamp"),
    brief: bool = typer.Option(False, help="Output compact summary instead of full JSON"),
    enrich: bool = typer.Option(False, help="Add first_name and company_name from leads API (use with --brief)"),
):
    """List emails (Unibox). Rate limited to 20 req/min."""
    params: dict = {}
    if limit is not None:
        params["limit"] = limit
    if starting_after is not None:
        params["starting_after"] = starting_after
    if search is not None:
        params["search"] = search
    if campaign_id is not None:
        params["campaign_id"] = campaign_id
    if list_id is not None:
        params["list_id"] = list_id
    if i_status is not None:
        params["i_status"] = i_status
    if eaccount is not None:
        params["eaccount"] = eaccount
    if is_unread is not None:
        params["is_unread"] = str(is_unread).lower()
    if has_reminder is not None:
        params["has_reminder"] = str(has_reminder).lower()
    if mode is not None:
        params["mode"] = mode
    if preview_only is not None:
        params["preview_only"] = str(preview_only).lower()
    if sort_order is not None:
        params["sort_order"] = sort_order
    if scheduled_only is not None:
        params["scheduled_only"] = str(scheduled_only).lower()
    if assigned_to is not None:
        params["assigned_to"] = assigned_to
    if lead is not None:
        params["lead"] = lead
    if company_domain is not None:
        params["company_domain"] = company_domain
    if marked_as_done is not None:
        params["marked_as_done"] = str(marked_as_done).lower()
    if email_type is not None:
        params["email_type"] = email_type
    if min_timestamp_created is not None:
        params["min_timestamp_created"] = min_timestamp_created
    if max_timestamp_created is not None:
        params["max_timestamp_created"] = max_timestamp_created

    client = InstantlyClient()
    result = client.get("/api/v2/emails", params=params)

    if brief:
        items = result.get("items", [])

        # Build lead lookup if --enrich is set
        lead_info: dict = {}
        if enrich and items:
            lead_emails = list({item.get("lead") for item in items if item.get("lead")})
            if lead_emails:
                leads_result = client.post("/api/v2/leads/list", json={"contacts": lead_emails, "limit": 100})
                for ld in leads_result.get("items", []):
                    email = ld.get("email")
                    if email:
                        lead_info[email] = {
                            "first_name": ld.get("first_name") or "",
                            "company_name": ld.get("company_name") or "",
                        }

        for item in items:
            text = (item.get("body") or {}).get("text", "")
            # Strip to first reply boundary for cleaner output
            for marker in ["\nOn ", "\n>", "\n---", "\n___", "\nFrom:"]:
                idx = text.find(marker)
                if idx > 0:
                    text = text[:idx]
            text = " ".join(text.split())
            brief_item = {
                "id": item.get("id"),
                "thread_id": item.get("thread_id"),
                "from": item.get("from_address_email"),
                "to": item.get("to_address_email_list"),
                "eaccount": item.get("eaccount"),
                "lead": item.get("lead"),
                "subject": item.get("subject"),
                "date": item.get("timestamp_email"),
                "body_preview": text[:500],
            }
            if enrich:
                info = lead_info.get(item.get("lead"), {})
                brief_item["first_name"] = info.get("first_name", "")
                brief_item["company_name"] = info.get("company_name", "")
            print(json.dumps(brief_item, ensure_ascii=False))
        nsa = result.get("next_starting_after")
        if nsa:
            print(json.dumps({"next_starting_after": nsa}))
    else:
        print(json.dumps(result, indent=2))


@emails_app.command()
def get(
    id: str = typer.Argument(help="UUID of the email to retrieve"),
):
    """Get a single email by ID."""
    client = InstantlyClient()
    result = client.get(f"/api/v2/emails/{id}")
    print(json.dumps(result, indent=2))


@emails_app.command("unread-count")
def unread_count():
    """Get the count of unread emails."""
    client = InstantlyClient()
    result = client.get("/api/v2/emails/unread/count")
    print(json.dumps(result, indent=2))


@emails_app.command("mark-read")
def mark_read(
    thread_id: str = typer.Argument(help="UUID of the thread to mark as read"),
):
    """Mark all emails in a thread as read."""
    client = InstantlyClient()
    result = client.post(f"/api/v2/emails/threads/{thread_id}/mark-as-read")
    print(json.dumps(result, indent=2))


@emails_app.command()
def update(
    id: str = typer.Argument(help="UUID of the email to update"),
    is_unread: Optional[int] = typer.Option(None, help="1 = unread, 0 = read"),
    reminder_ts: Optional[str] = typer.Option(None, help="Set reminder (ISO 8601 datetime), or 'null' to clear"),
):
    """Update an email (set unread status or reminder)."""
    payload: dict = {}
    if is_unread is not None:
        payload["is_unread"] = is_unread
    if reminder_ts is not None:
        payload["reminder_ts"] = None if reminder_ts == "null" else reminder_ts

    if not payload:
        print("Error: at least one of --is-unread or --reminder-ts is required.")
        raise typer.Exit(code=1)

    client = InstantlyClient()
    client.patch(f"/api/v2/emails/{id}", json=payload)
    print(json.dumps({"success": True}))
