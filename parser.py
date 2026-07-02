"""Parser for .http request files (Kulala/REST-Client style format)."""
import re
from dataclasses import dataclass, field

METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")
METHOD_LINE = re.compile(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)", re.IGNORECASE)


@dataclass
class HttpRequest:
    name: str
    method: str
    url: str
    headers: dict = field(default_factory=dict)
    body: str = ""


def substitute(text, variables):
    def replace(match):
        key = match.group(1)
        return variables.get(key, match.group(0))
    return VAR_PATTERN.sub(replace, text)


def parse_variables(lines):
    """Extract @name = value lines, return (variables, remaining_lines)."""
    variables = {}
    remaining = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@") and "=" in stripped:
            key, value = stripped[1:].split("=", 1)
            variables[key.strip()] = value.strip()
        else:
            remaining.append(line)
    return variables, remaining


def parse_block(block, variables):
    lines = block.splitlines()
    idx = 0

    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    name = None
    # If the first non-blank line isn't a METHOD line, treat it as the request name/comment
    if idx < len(lines) and not METHOD_LINE.match(lines[idx].strip()):
        name = lines[idx].strip().lstrip("#").strip()
        idx += 1
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1

    if idx >= len(lines):
        return None  # empty block, nothing to parse

    method_match = METHOD_LINE.match(lines[idx].strip())
    if not method_match:
        return None  # not a valid request block

    method = method_match.group(1).upper()
    url = substitute(method_match.group(2), variables)
    idx += 1

    headers = {}
    while idx < len(lines) and lines[idx].strip() != "":
        header_line = lines[idx].strip()
        if ":" in header_line:
            key, value = header_line.split(":", 1)
            headers[key.strip()] = substitute(value.strip(), variables)
        idx += 1

    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    body = "\n".join(lines[idx:]).strip()
    if body:
        body = substitute(body, variables)

    if name is None:
        name = f"{method} {url}"

    return HttpRequest(name=name, method=method, url=url, headers=headers, body=body)


def parse_file(path):
    with open(path, "r") as f:
        content = f.read()

    lines = content.splitlines()
    variables, lines = parse_variables(lines)

    text = "\n".join(lines)
    blocks = re.split(r"^\s*###.*$", text, flags=re.MULTILINE)

    requests_list = []
    for block in blocks:
        if not block.strip():
            continue
        req = parse_block(block, variables)
        if req:
            requests_list.append(req)

    return requests_list, variables

