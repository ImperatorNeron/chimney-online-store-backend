"""Helpers to mask personally identifiable information (PII) before logging.

We log usernames/emails/phones for debugging, but writing them in clear
text to stdout/log files is a privacy problem (and a GDPR concern for a
shop that stores customer contacts). These helpers keep just enough of a
value to be useful for debugging while hiding the sensitive part.

"""

from typing import Optional


def mask_email(email: Optional[str]) -> str:
    if not email:
        return "<none>"
    local, _, domain = email.partition("@")
    if not domain:
        # not a well-formed email; mask the whole thing
        return mask_generic(email)
    shown = local[0] if local else ""
    return f"{shown}***@{domain}"


def mask_phone(phone: Optional[str]) -> str:
    if not phone:
        return "<none>"
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) <= 4:
        return "*" * len(digits)
    # keep the last 2 digits only
    return "*" * (len(digits) - 2) + digits[-2:]


def mask_generic(value: Optional[str]) -> str:
    """Mask an arbitrary short identifier (e.g. username): keep first char."""
    if not value:
        return "<none>"
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "*" * (len(value) - 1)
