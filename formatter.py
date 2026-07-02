"""Pretty-prints HTTP responses. Uses rich if installed, else plain json.dumps."""
import json

try:
    from rich.console import Console
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False

IMPORTANT_HEADERS = [
    "Content-Type",
    "Content-Length",
    "Authorization",
    "WWW-Authenticate",
    "Location",
    "Server",
]


def filter_headers(headers):
    """Return only the important headers, preserving original casing/value from the response."""
    lookup = {k.lower(): (k, v) for k, v in headers.items()}
    return [lookup[name.lower()] for name in IMPORTANT_HEADERS if name.lower() in lookup]


def pretty_print(response, elapsed, req, verbose=False):
    status_line = f"{req.method} {req.url} -> {response.status_code} {response.reason} ({elapsed * 1000:.0f}ms)"
    content_type = response.headers.get("Content-Type", "")

    body_text = response.text
    is_json = "application/json" in content_type
    if is_json:
        try:
            body_text = json.dumps(response.json(), indent=2)
        except ValueError:
            is_json = False

    if RICH_AVAILABLE:
        color = "green" if response.ok else "red"
        console.print(f"[bold {color}]{status_line}[/bold {color}]")
        console.print("[bold]Headers:[/bold]")
        headers_to_show = response.headers.items() if verbose else filter_headers(response.headers)
        for k, v in headers_to_show:
            console.print(f"  [cyan]{k}[/cyan]: {v}")
        console.print()
        if is_json:
            console.print(Syntax(body_text, "json", theme="monokai", word_wrap=True))
        else:
            console.print(body_text)
    else:
        print(status_line)
        print("Headers:")
        headers_to_show = response.headers.items() if verbose else filter_headers(response.headers)
        for k, v in headers_to_show:
            print(f"  {k}: {v}")
        print()
        print(body_text)

