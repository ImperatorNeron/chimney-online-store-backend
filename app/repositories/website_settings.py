from app.models.website_settings import WebSiteSettings
from app.utils.sql_repository import BaseRepository


class WebSiteSettingsRepository(BaseRepository):
    model = WebSiteSettings
