# db/crud.py
from db.connection import get_supabase_client

client = get_supabase_client()

def fetch_all_records(table_name: str):
    response = client.table(table_name).select("*").execute()
    return response.data

def fetch_record_by_id(table_name: str, record_id: int):
    response = client.table(table_name).select("*").eq("id", record_id).execute()
    return response.data

def insert_record(table_name: str, record: dict):
    response = client.table(table_name).insert(record).execute()
    return response.data

def update_record(table_name: str, record_id: int, updates: dict):
    response = client.table(table_name).update(updates).eq("id", record_id).execute()
    return response.data

def delete_record(table_name: str, record_id: int):
    response = client.table(table_name).delete().eq("id", record_id).execute()
    return response.data