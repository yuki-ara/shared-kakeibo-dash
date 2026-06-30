import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = dbc.Container([
    dbc.Row(
        dbc.Col([
            html.Div([
                html.H1("共同家計簿アプリへようこそ！", className="display-5 fw-bold mb-2"),
                html.P("右上のメニューから選んでね 🌿", className="lead text-muted mb-0"),
            ], className="text-center py-5"),
        ], width=12)
    ),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("💳", style={"fontSize": "1.8rem"}),
                    html.H5("楽天カードの支払い", className="mt-2 mb-1 fw-bold"),
                    html.P("入力不要！毎月12日に明細が確定後、まとめてアップロードします。", className="text-muted mb-0 small"),
                ], className="text-center p-4"),
            ], className="h-100 shadow-sm border-0", style={"borderRadius": "16px", "background": "#f0faf5"}),
        ], width=12, md=4, className="mb-3"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("✏️", style={"fontSize": "1.8rem"}),
                    html.H5("その他の支払い", className="mt-2 mb-1 fw-bold"),
                    html.P("それ以外で支払ったものは、各自で「入力」ページから入力してね。", className="text-muted mb-0 small"),
                ], className="text-center p-4"),
            ], className="h-100 shadow-sm border-0", style={"borderRadius": "16px", "background": "#f0faf5"}),
        ], width=12, md=4, className="mb-3"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("🐰", style={"fontSize": "1.8rem"}),
                    html.H5("ウラウラヤハヤハ", className="mt-2 mb-1 fw-bold"),
                    html.P("いっしょにたのしくかけいぼ！", className="text-muted mb-0 small"),
                ], className="text-center p-4"),
            ], className="h-100 shadow-sm border-0", style={"borderRadius": "16px", "background": "#f0faf5"}),
        ], width=12, md=4, className="mb-3"),
    ], className="mb-4"),
    dbc.Row(
        dbc.Col(
            html.Img(
                src='assets/chiikawa-usagi.png',
                style={"maxWidth": "320px", "width": "100%", "height": "auto", "display": "block", "margin": "0 auto"},
            ),
            width=12,
            className="text-center pb-4",
        )
    ),
], fluid=True)