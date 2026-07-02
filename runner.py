"""Executes a parsed HttpRequest and times it."""
import time
import requests


def execute(req, timeout=30):
    kwargs = {"headers": req.headers, "timeout": timeout}
    if req.body:
        kwargs["data"] = req.body.encode("utf-8")

    start = time.time()
    response = requests.request(req.method, req.url, **kwargs)
    elapsed = time.time() - start
    return response, elapsed

