# Instantly CLI

A Python CLI tool for the Instantly API v2, designed to be used by AI agents via shell commands.

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd instantly-cli
pip3 install -e .

# 2. Configure API key (one-time)
instantly configure --api-key "YOUR_INSTANTLY_API_KEY"

# 3. Read SKILL.md for the full agent playbook
```

## Agent Playbook

**Read `SKILL.md` before doing anything.** It contains:
- The daily workflow (fetch, read, reply, mark as read)
- Step-by-step instructions with exact commands
- Reply guidelines and tone
- Business context about EasyVC (features, pricing, calendar link)
- Reply templates in `templates/` and when to use each one

## Architecture

```
instantly-cli/
  instantly/
    __init__.py
    cli.py          # main entry point, Typer app
    client.py       # API wrapper (auth from ~/.instantly/config.json or INSTANTLY_API_KEY env var)
    commands/
      emails.py     # emails subcommands (list, get, reply, forward, update, unread-count, mark-read)
      leads.py      # leads subcommands (create, get, list, update, update-interest)
  templates/        # reply templates (markdown, convert to HTML before sending)
  SKILL.md          # full agent playbook
  pyproject.toml    # pip3 install -e . gives the `instantly` command
```

## Auth

The API key is resolved in this order:
1. `INSTANTLY_API_KEY` environment variable (if set, takes priority)
2. `~/.instantly/config.json` (written by `instantly configure`)

## Available Commands

### Emails

| Command | Description |
|---|---|
| `instantly emails list` | List emails (supports `--brief --enrich` for agent use) |
| `instantly emails get <id>` | Get a single email by UUID |
| `instantly emails reply` | Reply to an email |
| `instantly emails forward` | Forward an email |
| `instantly emails update <id>` | Update email (set unread status or reminder) |
| `instantly emails unread-count` | Get count of unread emails |
| `instantly emails mark-read <thread_id>` | Mark all emails in a thread as read |

### Leads

| Command | Description |
|---|---|
| `instantly leads create` | Create a new lead |
| `instantly leads get <id>` | Get a single lead by UUID |
| `instantly leads list` | List/search leads with filters |
| `instantly leads update <id>` | Update a lead |
| `instantly leads update-interest` | Update lead interest status |

### Config

| Command | Description |
|---|---|
| `instantly configure` | Save API key to `~/.instantly/config.json` |

Run any command with `--help` for full options.

## Deployment

1. Push to GitHub
2. On EC2: `git clone` + `pip3 install -e .`
3. Run `instantly configure --api-key "YOUR_KEY"` once
4. AI agents invoke via shell: `instantly emails list --is-unread --i-status 1 --brief --enrich`
