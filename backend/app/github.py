import hashlib
import hmac

import httpx


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


def fetch_pull_request_diff(repository: str, number: int, token: str = "") -> str:
    headers = {"Accept": "application/vnd.github.v3.diff", "User-Agent": "ReviewForge/0.1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = httpx.get(
        f"https://api.github.com/repos/{repository}/pulls/{number}", headers=headers, timeout=30
    )
    response.raise_for_status()
    return response.text

