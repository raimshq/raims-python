from __future__ import annotations

import hashlib
import hmac
import re
import time
from collections.abc import Mapping
from typing import Any

from ._errors import SignatureVerificationError
from ._validation import parse_json

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def _header(headers: Mapping[str, Any], name: str) -> str:
    if not isinstance(headers, Mapping):
        raise SignatureVerificationError("Webhook headers must be an HTTP header collection.")
    multi_items = getattr(headers, "multi_items", None)
    pairs = multi_items() if callable(multi_items) else headers.items()
    values = [value for key, value in pairs if isinstance(key, str) and key.lower() == name]
    if len(values) != 1:
        raise SignatureVerificationError(
            "A webhook signing header is missing or occurs more than once."
        )
    value = values[0]
    if isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    if not isinstance(value, str) or not value or re.search(r"[\x00-\x08\x0a-\x1f\x7f]", value):
        raise SignatureVerificationError("A webhook signing header is invalid.")
    return value


def _secret(secret: str) -> bytes:
    if not isinstance(secret, str) or not re.fullmatch(r"whsec_[0-9A-Za-z]{1,43}", secret):
        raise SignatureVerificationError("The webhook signing secret is invalid.")
    encoded = secret[6:]
    if len(encoded) > 1 and encoded[0] == "0":
        raise SignatureVerificationError("The webhook signing secret is invalid.")
    number = 0
    for char in encoded:
        number = number * 62 + _ALPHABET.index(char)
    if number >= 1 << 256:
        raise SignatureVerificationError("The webhook signing secret is invalid.")
    return number.to_bytes(32, "little")


class Webhook:
    @staticmethod
    def verify_signature(
        payload: bytes | str,
        headers: Mapping[str, Any],
        secret: str,
        *,
        tolerance: int = 300,
        now: int | None = None,
    ) -> None:
        if type(tolerance) is not int or tolerance < 0:
            raise ValueError("Webhook tolerance must be a non-negative integer.")
        current = int(time.time()) if now is None else now
        if type(current) is not int or current < 0:
            raise ValueError("Webhook now must be a non-negative integer.")
        if not isinstance(payload, (str, bytes)):
            raise SignatureVerificationError(
                "The webhook body must contain the original HTTP bytes."
            )
        try:
            body = payload.encode("utf-8") if isinstance(payload, str) else payload
        except UnicodeError:
            raise SignatureVerificationError("The webhook body is not valid UTF-8.") from None
        delivery_id = _header(headers, "webhook-id")
        timestamp = _header(headers, "webhook-timestamp")
        signatures = _header(headers, "webhook-signature")
        if not re.fullmatch(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", delivery_id):
            raise SignatureVerificationError("The webhook delivery ID is invalid.")
        if not re.fullmatch(r"[0-9]{1,12}", timestamp) or abs(int(timestamp) - current) > tolerance:
            raise SignatureVerificationError(
                "The webhook timestamp is invalid or outside the allowed tolerance."
            )
        expected = hmac.new(
            _secret(secret), f"{delivery_id}.{timestamp}.".encode("ascii") + body, hashlib.sha256
        ).digest()
        matched = False
        for candidate in signatures.split(","):
            match = re.fullmatch(r"v1=([0-9a-fA-F]{64})", candidate.strip(), flags=re.IGNORECASE)
            if match:
                matched |= hmac.compare_digest(expected, bytes.fromhex(match[1]))
        if not matched:
            raise SignatureVerificationError("No webhook signature matches the configured secret.")

    @staticmethod
    def construct_event(
        payload: bytes | str,
        headers: Mapping[str, Any],
        secret: str,
        *,
        tolerance: int = 300,
        now: int | None = None,
    ) -> dict[str, Any]:
        Webhook.verify_signature(payload, headers, secret, tolerance=tolerance, now=now)
        try:
            event = parse_json(payload.encode("utf-8") if isinstance(payload, str) else payload)
        except (ValueError, UnicodeError, RecursionError):
            raise SignatureVerificationError(
                "The authenticated webhook body is not valid JSON."
            ) from None
        if not isinstance(event, dict):
            raise SignatureVerificationError(
                "The authenticated webhook body must be a JSON object."
            )
        return event
