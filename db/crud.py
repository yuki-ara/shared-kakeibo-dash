# db/crud.py
from db.connection import get_supabase_client

ALLOWED_TABLES = {
    'shared_kakeibo',
    'shared_kakeibo_view',
    'shared_kakeibo_category',
    'shared_kakeibo_shop',
    'shared_kakeibo_payment',
}

client = get_supabase_client()

def _validate_table(table_name: str):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"不正なテーブル名: {table_name}")

def fetch_all_records(table_name: str):
    _validate_table(table_name)
    try:
        response = client.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] fetch_all_records({table_name}): {e}")
        return []

def fetch_record_by_id(table_name: str, record_id: int):
    _validate_table(table_name)
    try:
        response = client.table(table_name).select("*").eq("id", record_id).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] fetch_record_by_id({table_name}, {record_id}): {e}")
        return []

def insert_record(table_name: str, record: dict):
    _validate_table(table_name)
    try:
        response = client.table(table_name).insert(record).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] insert_record({table_name}): {e}")
        raise

def update_record(table_name: str, record_id: int, updates: dict):
    _validate_table(table_name)
    try:
        response = client.table(table_name).update(updates).eq("id", record_id).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] update_record({table_name}, {record_id}): {e}")
        raise

def delete_record(table_name: str, record_id: int):
    _validate_table(table_name)
    try:
        response = client.table(table_name).delete().eq("id", record_id).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] delete_record({table_name}, {record_id}): {e}")
        raise
