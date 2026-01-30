import typer

from instantly.client import save_api_key
from instantly.commands.emails import emails_app
from instantly.commands.leads import leads_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(emails_app, name="emails")
app.add_typer(leads_app, name="leads")


@app.command()
def configure(
    api_key: str = typer.Option(..., prompt="Instantly API key", help="Your Instantly API key"),
):
    """Save your Instantly API key to ~/.instantly/config.json."""
    save_api_key(api_key)
    print("API key saved. You can now use all commands without setting INSTANTLY_API_KEY.")


if __name__ == "__main__":
    app()
