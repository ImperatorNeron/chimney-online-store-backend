from pydantic import BaseModel, Field


class ReadWebSiteSettingsSchema(BaseModel):
    manufacturer_discount: float = Field(ge=0, le=100)
    seller_markup: float = Field(ge=0, le=100)


class UpdateWebSiteSettingsSchema(BaseModel):
    manufacturer_discount: float | None = Field(None, ge=0, le=100)
    seller_markup: float | None = Field(None, ge=0, le=100)
