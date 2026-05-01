from typing import Optional

from pydantic import BaseModel, Field


class ReadWebSiteSettingsSchema(BaseModel):
    manufacturer_discount: float = Field(ge=0, le=100)
    seller_markup: float = Field(ge=0, le=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    work_schedule: Optional[str] = None
    telegram_url: Optional[str] = None
    facebook_url: Optional[str] = None


class UpdateWebSiteSettingsSchema(BaseModel):
    manufacturer_discount: Optional[float] = Field(None, ge=0, le=100)
    seller_markup: Optional[float] = Field(None, ge=0, le=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=150)
    address: Optional[str] = Field(None, max_length=300)
    work_schedule: Optional[str] = Field(None, max_length=200)
    telegram_url: Optional[str] = Field(None, max_length=300)
    facebook_url: Optional[str] = Field(None, max_length=300)
