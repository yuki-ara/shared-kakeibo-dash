import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from db.crud import fetch_all_records

dash.register_page(__name__, path='/')

QUICK_LINKS = [
    {"icon": "✏️", "label": "入力", "desc": "支出・収入を登録する", "href": "/input"},
    {"icon": "📋", "label": "一覧", "desc": "登録済みデータを確認・編集する", "href": "/datatable"},
    {"icon": "📊", "label": "分析", "desc": "月別の収支やカテゴリ別集計を見る", "href": "/analytics"},
]

def format_yen_jp(value: float) -> str:
    """日本式の万・億単位区切りで金額を表示する（例: 10005 -> '1万5円'）。"""
    value = int(round(value))
    sign = '-' if value < 0 else ''
    value = abs(value)
    oku, rest = divmod(value, 100_000_000)
    man, yen = divmod(rest, 10_000)
    parts = []
    if oku:
        parts.append(f"{oku}億")
    if man or (oku and yen):
        parts.append(f"{man}万")
    if yen or not parts:
        parts.append(f"{yen:,}")
    return f"{sign}{''.join(parts)}円"

layout = dbc.Container([
    dcc.Location(id='home-url', refresh=False),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("共同家計簿アプリへようこそ！", className="display-5 fw-bold mb-2"),
                html.P("右上のメニューから選んでね 🌿", className="lead text-muted mb-0"),
            ], className="text-center text-md-start"),
        ], width=12, md=6, className="d-flex flex-column justify-content-center"),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Span("🐰", style={"fontSize": "1.8rem"}),
                    html.H5("ウラウラヤハヤハ", className="mt-2 mb-1 fw-bold"),
                    html.P("いっしょにたのしくかけいぼ！", className="text-muted mb-0 small"),
                ], className="text-center p-4"),
            ], className="shadow-sm border-0 mb-3", style={"borderRadius": "16px", "background": "#f0faf5"}),
            html.Img(
                src='assets/chiikawa-usagi.png',
                style={"maxWidth": "200px", "width": "100%", "height": "auto", "display": "block", "margin": "0 auto"},
            ),
        ], width=12, md=6, className="text-center py-4"),
    ], className="align-items-center"),
    dbc.Row([
        dbc.Col([
            dcc.Link([
                dbc.Card([
                    dbc.CardBody([
                        html.Span(link["icon"], style={"fontSize": "1.8rem"}),
                        html.H5(link["label"], className="mt-2 mb-1 fw-bold"),
                        html.P(link["desc"], className="text-muted mb-0 small"),
                    ], className="text-center p-4"),
                ], className="h-100 shadow-sm border-0", style={"borderRadius": "16px"}),
            ], href=link["href"], className="text-decoration-none text-reset"),
        ], width=12, md=4, className="mb-3")
        for link in QUICK_LINKS
    ], className="mb-4"),
    dbc.Row(
        dbc.Col([
            html.H5("最近の取引", className="mb-3 text-muted"),
            html.Div(id='home-recent-transactions'),
        ], width=12, md=10, className="mx-auto"),
        className="d-none d-md-flex mb-4",
    ),
], fluid=True)

RECENT_TRANSACTIONS_LIMIT = 8

@callback(
    Output('home-recent-transactions', 'children'),
    Input('home-url', 'pathname'),
)
def update_home_recent_transactions(_pathname):
    data = fetch_all_records('shared_kakeibo_view')
    if not data:
        return html.P("データがありません", className="text-muted")

    rows = sorted(data, key=lambda r: (r.get('date') or '', r.get('created_at') or ''), reverse=True)
    rows = rows[:RECENT_TRANSACTIONS_LIMIT]

    table_rows = []
    for r in rows:
        income, expense = r.get('income') or 0, r.get('expense') or 0
        if income:
            amount_text, amount_class = f"+{format_yen_jp(income)}", "text-success"
        else:
            amount_text, amount_class = f"-{format_yen_jp(expense)}", "text-danger"
        table_rows.append(html.Tr([
            html.Td(r.get('date')),
            html.Td(r.get('item')),
            html.Td(r.get('category')),
            html.Td(amount_text, className=amount_class),
            html.Td(r.get('editor')),
        ]))

    return dbc.Table([
        html.Thead(html.Tr([html.Th(h) for h in ["日付", "品目", "カテゴリ", "金額", "担当者"]])),
        html.Tbody(table_rows),
    ], hover=True, responsive=True, size="sm")