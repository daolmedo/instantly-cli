# Instantly CLI

## Overview

A Python CLI tool for the Instantly API v2, designed to be used by AI agents via shell commands.

## Architecture

Python package using Typer with subcommands:

```
instantly-cli/
  instantly/
    __init__.py
    cli.py          # main entry point, Typer app
    client.py       # thin API wrapper (auth, requests, error handling)
    commands/
      campaigns.py
      leads.py
      emails.py
      accounts.py
  pyproject.toml    # pip install -e . gives the `instantly` command
```

- Subcommand structure: `instantly emails list --limit 10`
- JSON output by default (agent-friendly)
- `client.py` handles auth/retries; commands stay thin
- Adding a new endpoint = adding a function

## API Details

- **Base URL:** `https://api.instantly.ai/`
- **API Version:** v2
- **Auth:** `Authorization: Bearer <token>` header
- **API key env var:** `INSTANTLY_API_KEY`

## API Documentation

All API docs are in `api-docs/`:

- `Instantly Docs.md` — top-level entry point
- `Email Endpoint.md` — index for all email endpoints (maps to `api-docs/email/` folder)
- `Lead Endpoint.md` — index for all lead endpoints (maps to `api-docs/lead/` folder)
- `api-docs/email/` — individual email endpoint docs (reply, forward, list, get, update, unread count, mark read)
- `api-docs/lead/` — individual lead endpoint docs (create, delete, list, get, update, update interest status)

## Deployment

1. Push to GitHub
2. On EC2: `git clone` + `pip install -e .`
3. Set `export INSTANTLY_API_KEY="..."` on the instance
4. AI agents invoke via shell: `instantly emails list --limit 10`
