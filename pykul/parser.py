"""Parser for .http request files (Kulala/REST-Client style format)."""
import re
from dataclasses import dataclass, field

METHOD_LINE = re.compile(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)", re.IGNORECASE)
SEPARATOR_LINE = re.compile(r"^\s*###")
VAR_LINE = re.compile(r"^\s*@(\w+)\s*=\s*(.*)$")
VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class HttpRequest:
    name: str
    method: str
    url: str
    headers: dict = field(default_factory=dict)
    body: str = ""
    line: int = 0  # 1-indexed line number where this request block starts in the source file


def substitute(text, variables):
    def replace(match):
        key = match.group(1)
        return variables.get(key, match.group(0))
    return VAR_PATTERN.sub(replace, text)


def parse_block(block_lines, variables):
    lines = list(block_lines)
    idx = 0

    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    name = None
    if idx < len(lines) and not METHOD_LINE.match(lines[idx].strip()):
        name = lines[idx].strip().lstrip("#").strip()
        idx += 1
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1

    if idx >= len(lines):
        return None

    method_match = METHOD_LINE.match(lines[idx].strip())
    if not method_match:
        return None

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
        lines = [line.rstrip("\n") for line in f.readlines()]

    # Variables can be defined anywhere (usually at the top); collect them first.
    variables = {}
    for line in lines:
        match = VAR_LINE.match(line)
        if match:
            variables[match.group(1)] = match.group(2).strip()

    separator_indices = [i for i, line in enumerate(lines) if SEPARATOR_LINE.match(line)]

    blocks = []
    if separator_indices:
        for i, sep_i in enumerate(separator_indices):
            start = sep_i + 1
            end = separator_indices[i + 1] if i + 1 < len(separator_indices) else len(lines)
            blocks.append((start + 1, lines[start:end]))  # start+1 => 1-indexed line number

    requests_list = []
    for start_line, block_lines in blocks:
        # Variable-definition lines can appear inside a block too; strip them before parsing.
        filtered = [l for l in block_lines if not VAR_LINE.match(l)]
        req = parse_block(filtered, variables)
        if req:
            req.line = start_line
            requests_list.append(req)

    return requests_list, variables


def find_request_at_line(requests_list, line_no):
    """Return the request whose block contains the given 1-indexed line number.

    Used for editor integration (e.g. Nvim 'run request under cursor').
    """
    candidates = [r for r in requests_list if r.line <= line_no]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r.line)
