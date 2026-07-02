# PyKul

A lightweight, Kulala-inspired HTTP client for the terminal — built for **Termux** and **Neovim** workflows.

Write requests in plain `.http` files and execute them directly from the command line or your editor.

---

## Features

- Simple `.http` file format
- Multiple requests per file
- Run a request by index
- Run a request by name
- List available requests
- Pretty JSON output (when `rich` is installed)
- Installable as a Python CLI (`pykul`)
- Designed to work well on Termux
- Easy Neovim integration

---

## Installation

Clone the repository:

```bash
git clone https://github.com/pransisomsim/PyKul.git
cd PyKul
```

Install in editable mode (recommended while developing):

```bash
python -m pip install -e .
```

Or install the dependencies manually:

```bash
pip Install -r requirements.txt
```

---

## `.http` File Format

```http
### Get Post
GET https://jsonplaceholder.typicode.com/posts/1

### Get User
GET https://jsonplaceholder.typicode.com/users/1

### Create Post
POST https://jsonplaceholder.typicode.com/posts
Content-Type: application/json

{
  "title": "Hello",
  "body": "World",
  "userId": 1
}
```

Each request is separated by `###`.

The first line after `###` may be a display name.

Headers are written after the request line.

A blank line separates headers from the request body.

---

## CLI Usage

List requests:

```bash
pykul requests.http -l
```

Run a request by index:

```bash
pykul requests.http -i 2
```

Run a request by name:

```bash
pykul requests.http -n "Create Post"
```

If the file contains only one request:

```bash
pykul requests.http
```

Example output:

```text
GET https://jsonplaceholder.typicode.com/posts/1 -> 200 OK (243ms)

Headers:
  Content-Type: application/json
  Server: cloudflare

{
  ...
}
```

---

## Neovim Integration

Example mapping:

```lua
vim.keymap.set("n", "<leader>rr", function()
    local file = vim.fn.expand("%:p")
    vim.cmd("!pykul " .. vim.fn.shellescape(file))
end, {
    desc = "Run HTTP request",
})
```

Future versions will support running the request under the cursor and displaying responses in a dedicated Neovim window.

---

## Roadmap

### v0.2

- [ ] Run request under cursor
- [ ] Dedicated Neovim response window
- [ ] Environment variables
- [ ] `.env` support
- [ ] Response history

### v0.3

- [ ] File uploads
- [ ] Cookies & sessions
- [ ] GraphQL
- [ ] Response assertions
- [ ] Request chaining

---

## Why PyKul?

PyKul aims to provide a fast, lightweight alternative to GUI API clients for developers who live in the terminal—especially those using **Termux** and **Neovim**.

Instead of switching to a separate application, you keep your API requests alongside your project and execute them with a single command.

---

## License

MIT
