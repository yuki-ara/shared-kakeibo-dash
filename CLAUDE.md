# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

The app runs as a systemd service (`shared-kakeibo-dash.service`) and is **always active** on this Raspberry Pi. Do not start a separate process.

```bash
sudo systemctl restart shared-kakeibo-dash   # apply code changes
sudo systemctl status shared-kakeibo-dash    # check status / last logs
journalctl -u shared-kakeibo-dash -f         # tail live logs
journalctl -u shared-kakeibo-dash -n 50      # last 50 log lines
```

App is served at `http://<host>:8050`. Config: `config/secrets.env` — requires `SUPABASE_URL` and `SUPABASE_KEY`.

## Architecture

**App factory:** `run.py` → `app/__init__.py:create_app()` bootstraps the Dash app. Pages under `app/pages/` are auto-discovered at startup via `importlib`; each file calls `dash.register_page(__name__)` at module level and exports a `layout` variable with its callbacks.

**Layout shell:** `app/layout.py` defines the top-level navbar + `dash.page_container`. It handles the responsive offcanvas mobile nav callback (toggler opens, nav-link click closes).

**DB layer:**
- `db/connection.py` — creates the Supabase client from `config/secrets.env`
- `db/crud.py` — thin wrappers (fetch/insert/update/delete) guarded by an `ALLOWED_TABLES` allowlist. All writes go to `shared_kakeibo`; reads for analytics use the `shared_kakeibo_view` DB view.

**Pages:**
- `home.py` — static welcome page (`path='/'`)
- `input.py` — form to insert a single record into `shared_kakeibo`
- `datatable.py` — paginated table with inline edit/delete modals; data refreshes on button click
- `analytics.py` — charts and summary cards; all data fetched on button click via `shared_kakeibo_view`

## Key patterns

**Dropdown options load once at import time** (not per-callback) in `input.py` and `datatable.py`:
```python
category_options = [{'label': c['item'], 'value': c['id']} for c in fetch_all_records('shared_kakeibo_category')]
```
If reference data changes, a server restart is required to pick up new values.

**Irregular categories** (`analytics.py`): `IRREGULAR_CATEGORIES = ['家具・家電', '交際費', '旅行費', '冠婚葬祭', 'その他']` are excluded from the main stacked bar / pie charts and shown separately as monthly summary cards.

**`shared_kakeibo` schema** (main table): `id` (UUID), `date`, `income`, `expense`, `item`, `category` (FK→`shared_kakeibo_category.id`), `shop` (FK→`shared_kakeibo_shop.id`), `payment` (FK→`shared_kakeibo_payment.id`), `note`, `created_at`, `editor`.

**`shared_kakeibo_view`** — denormalized read view used by analytics and datatable; returns label strings for category/shop/payment instead of IDs.

## Rakuten card bulk import

Monthly workflow (after 12th — when statement is confirmed):
1. Download CSV from [楽天e-navi](https://www.rakuten-card.co.jp/e-navi/)
2. Process: `python3 rakuten-card-analysis/process-credit-statement.py <csv>`
3. Manually fill `item`, `category`, `shop` columns in the generated `processed_*.csv`
4. Bulk insert: `python3 -m rakuten-card-analysis.bulk-insert-csv <processed_csv>`

To delete all Rakuten card records (payment id=1):
```bash
curl -X DELETE 'https://yuuirnewmsmnbfsdsqdn.supabase.co/rest/v1/shared_kakeibo?payment=eq.1' \
    -H "apikey: ${SUPABASE_KEY}" -H "Authorization: Bearer ${SUPABASE_KEY}"
```
