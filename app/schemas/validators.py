import re

from pydantic import field_validator

from app.core.constants import SLUG_REGEX


class SlugValidatorMixin:
    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and not re.match(SLUG_REGEX, v):
            raise ValueError("Slug має містити тільки a-z, 0-9, '-' та '_'")
        return v.lower() if v else v
