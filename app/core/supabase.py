from supabase import Client, create_client

from app.core.settings import settings


supabase_client: Client = create_client(settings.bucket.supabase_url, settings.bucket.supabase_key)
