import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv(dotenv_path="config/secrets.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SupabaseのURLまたはキーが設定されていません")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


if __name__ == "__main__":
    client = get_supabase_client()
    all_data = client.table("shared_kakeibo").select("*").execute()
    print(all_data.data)


