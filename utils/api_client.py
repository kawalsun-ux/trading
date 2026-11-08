"""Zero-dep HTTP API client (stdlib only). Ingested from api-anything client pattern."""
import json, os, socket, time, urllib.error, urllib.parse, urllib.request
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

DEFAULT_URL = "http://127.0.0.1:8787"
LOOPBACK = {"127.0.0.1", "localhost", "::1", "[::1]"}

Fields = Union[str, Sequence[str]]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class ApiError(Exception):
    def __init__(self, status, message, body=None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


class ApiClient:
    """Minimal HTTP client for a JSON API (stdlib only)."""

    def __init__(self, base_url=None, token=None, timeout=30.0):
        self.base_url = (base_url or os.environ.get("API_URL") or DEFAULT_URL).rstrip("/")
        self.timeout = timeout
        self._token = token
        host = urllib.parse.urlsplit(self.base_url).hostname or ""
        handlers = [_NoRedirect()]
        if host in LOOPBACK or f"[{host}]" in LOOPBACK:
            handlers.append(urllib.request.ProxyHandler({}))
        self._opener = urllib.request.build_opener(*handlers)

    def _auth_token(self):
        return self._token or os.environ.get("API_TOKEN")

    def _send(self, method, path, body=None, query=None, timeout=None):
        url = self.base_url + path
        if query:
            params = {k: v for k, v in query.items() if v is not None}
            if params:
                url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        token = self._auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        wait = self.timeout if timeout is None else timeout
        try:
            with self._opener.open(req, timeout=wait) as r:
                return r.status, _parse(r.read())
        except urllib.error.HTTPError as e:
            try:
                raw = e.read()
            finally:
                e.close()
            return e.code, _parse(raw)
        except urllib.error.URLError as e:
            raise ConnectionError(f"no server at {self.base_url}: {e.reason}")
        except (socket.timeout, TimeoutError):
            raise TimeoutError(f"no answer within {wait}s")

    def get(self, path, query=None, timeout=None):
        status, payload = self._send("GET", path, query=query, timeout=timeout)
        if 200 <= status < 300:
            return payload
        raise ApiError(status, str(payload))

    def post(self, path, body=None, query=None, timeout=None):
        status, payload = self._send("POST", path, body=body, query=query, timeout=timeout)
        if 200 <= status < 300:
            return payload
        raise ApiError(status, str(payload))

    def health(self):
        return self.get("/v1/health")


def _parse(raw):
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except ValueError:
        return text