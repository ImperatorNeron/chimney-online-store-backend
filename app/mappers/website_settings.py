from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.website_settings import WebSiteSettings
from app.schemas.website_settings import ReadWebSiteSettingsSchema, UpdateWebSiteSettingsSchema


class WebSiteSettingsReadMapper(BaseReadMapper[WebSiteSettings, ReadWebSiteSettingsSchema]):

    @staticmethod
    def to_dto(orm_obj: WebSiteSettings) -> ReadWebSiteSettingsSchema:
        return ReadWebSiteSettingsSchema(
            manufacturer_discount=float(orm_obj.manufacturer_discount),
            seller_markup=float(orm_obj.seller_markup),
        )


class WebSiteSettingsUpdateMapper(BaseUpsertMapper[WebSiteSettings, UpdateWebSiteSettingsSchema]):
    pass
