import dash
from dash import html, Output, Input, State
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("家計簿アプリ", className="ms-2"),
            
            # 中〜大画面用のナビリンク（常時表示）
            dbc.Nav(
                [
                    dbc.NavLink(page['name'], href=page['relative_path'], active="exact")
                    for page in dash.page_registry.values()
                ],
                className="d-none d-md-flex",
                pills=True,
            ),

            # 小画面用ハンバーガーアイコンとOffcanvasメニュー
            dbc.NavbarToggler(id="navbar-toggler", className="ms-auto d-md-none"),
            dbc.Offcanvas(
                dbc.Nav(
                    [
                        dbc.NavLink(page['name'], href=page['relative_path'], active="exact", id={"type": "nav-link", "index": page['name']})
                        for page in dash.page_registry.values()
                    ],
                    vertical=True,
                    pills=True,
                ),
                id="offcanvas-scrollable",
                scrollable=True,
                title="メニュー",
                is_open=False,
                backdrop=True,
                placement="end",
            ),
        ]),
        color="primary",
        dark=True,
        expand="md",
    ),
    dbc.Container([
        html.Div(dash.page_container, className="p-4")
    ], id="page-content"),
], id="app-container")

@dash.callback(
    Output("offcanvas-scrollable", "is_open"),
    [
        Input("navbar-toggler", "n_clicks"),
        Input({"type": "nav-link", "index": dash.ALL}, "n_clicks"),
    ],
    State("offcanvas-scrollable", "is_open"),
    prevent_initial_call=True
)
def toggle_offcanvas_scrollable(n1, link_cliked, is_open):
    if n1:
        return not is_open
    if link_cliked:
        return False
    return is_open
