# app/__init__.py
import dash
from dash import Dash
import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

def create_app() -> Dash:
    app = dash.Dash(
        __name__, 
        suppress_callback_exceptions=True, 
        use_pages=True, 
        external_stylesheets=[dbc.themes.MINTY, dbc_css],  # 初期テーマ
    )
    app.title = "家計簿アプリ"

    # Dynamically import all modules in app/pages to register Dash pages
    import importlib
    import os
    import pathlib
    pages_dir = pathlib.Path(__file__).parent / "pages"
    for file in os.listdir(pages_dir):
        if file.endswith(".py") and not file.startswith("__"):
            importlib.import_module(f"app.pages.{file[:-3]}")

    from app.layout import layout
    app.layout = layout

    return app


