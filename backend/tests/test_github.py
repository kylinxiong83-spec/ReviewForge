import hashlib
import hmac

from app.github import verify_signature


def test_webhook_signature_verification() -> None:
    payload = b'{"action":"opened"}'
    secret = "test-secret"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, signature, secret)
    assert not verify_signature(payload + b"x", signature, secret)

