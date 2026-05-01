import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.core.settings import settings


class SupabaseUploadRotatingHandler(TimedRotatingFileHandler):
    """Rotates logs daily.

    On prod, uploads rotated file to Supabase bucket.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]

        current_time = self.rolloverAt - self.interval
        time_tuple = self.converter(current_time)
        dfn = self.rotation_filename(
            self.baseFilename + "." + self.suffix % time_tuple if hasattr(self, 'suffix') else self.baseFilename + ".1",
        )

        super().doRollover()

        if settings.environment == "prod" and os.path.exists(dfn):
            self._upload_to_supabase(dfn)

    def _upload_to_supabase(self, file_path: str):
        try:
            from app.core.supabase import supabase_client

            filename = os.path.basename(file_path)
            bucket_path = f"logs/{filename}"

            with open(file_path, "rb") as f:
                supabase_client.storage.from_(settings.bucket.name).upload(
                    bucket_path, f.read(),
                )

            logging.getLogger(__name__).info(
                "Uploaded rotated log to Supabase: %s", bucket_path,
            )
        except Exception as e:
            logging.getLogger(__name__).error(
                "Failed to upload log to Supabase: %s", e,
            )


def setup_logging():
    log_dir = settings.logging.log_dir
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = str(settings.logging.log_file_path)

    handler_cls = SupabaseUploadRotatingHandler if settings.environment == "prod" else TimedRotatingFileHandler

    rotating_handler = handler_cls(
        filename=log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    rotating_handler.suffix = "%Y-%m-%d"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    rotating_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=settings.logging.log_level,
        handlers=[rotating_handler, console_handler],
    )
