import base64
import io
from collections import Counter

import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

from db.crud import fetch_all_records

dash.register_page(__name__, path='/rakuten-check', name='カード照合')

RAKUTEN_PAYMENT_LABEL = '楽天カード'
CSV_REQUIRED_COLUMNS = {'利用日', '利用店名・商品名', '利用金額'}


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


def fetch_rakuten_data():
    data = fetch_all_records('shared_kakeibo_view')
    if not data:
        return pd.DataFrame(columns=['date', 'expense', 'item', 'shop', 'payment'])
    df = pd.DataFrame(data)
    df = df[df['payment'] == RAKUTEN_PAYMENT_LABEL].copy()
    df['expense'] = pd.to_numeric(df['expense'], errors='coerce').fillna(0)
    return df


layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("楽天カード明細照合"), width=12, className="mb-2"),
        dbc.Col(
            html.P(
                "メール自動登録で漏れがないか、月に一度 e-navi の確定金額・CSVと照らし合わせてください。",
                className="text-muted",
            ),
            width=12,
        ),
    ], className="mt-3"),

    dbc.Row([
        dbc.Col([
            html.H5("月別合計", className="mb-3 text-muted"),
            dbc.Button("更新", id="rakuten-refresh-btn", color="primary", size="sm", className="mb-3"),
            dcc.Graph(id='rakuten-monthly-graph'),
            html.Div(id='rakuten-monthly-table'),
        ], width=12, className="mb-4"),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H5("CSVで照合", className="mb-3 text-muted"),
            html.P(
                "e-naviからダウンロードした明細CSVをアップロードすると、家計簿に登録されていない明細を検出します。",
                className="text-muted small",
            ),
            dcc.Upload(
                id='rakuten-csv-upload',
                children=html.Div(['CSVをドラッグ&ドロップ、または ', html.A('ファイルを選択')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '8px',
                    'textAlign': 'center', 'margin': '10px 0',
                },
                multiple=False,
            ),
            html.Div(id='rakuten-csv-result'),
        ], width=12, className="mb-4"),
    ]),
], fluid=True)


@callback(
    Output('rakuten-monthly-graph', 'figure'),
    Output('rakuten-monthly-table', 'children'),
    Input('rakuten-refresh-btn', 'n_clicks'),
)
def update_monthly_summary(_n_clicks):
    df = fetch_rakuten_data()
    if df.empty:
        return px.bar(title='楽天カード 月別支出合計（データなし）'), html.P("データがありません", className="text-muted")

    df['YearMonth'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    monthly = df.groupby('YearMonth', as_index=False).agg(
        合計=('expense', 'sum'),
        件数=('expense', 'count'),
    ).sort_values('YearMonth')
    monthly['合計表示'] = monthly['合計'].apply(format_yen_jp)

    fig = px.bar(
        monthly, x='YearMonth', y='合計', text='合計表示',
        title='楽天カード 月別支出合計',
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(hovertemplate='%{x}<br>%{text}<extra></extra>')
    fig.update_layout(xaxis_title='年月', yaxis_title='金額')

    table = dbc.Table.from_dataframe(
        monthly[['YearMonth', '合計表示', '件数']].rename(columns={'YearMonth': '年月', '合計表示': '合計'}).sort_values('年月', ascending=False),
        striped=True, bordered=True, hover=True, responsive=True,
    )
    return fig, table


@callback(
    Output('rakuten-csv-result', 'children'),
    Input('rakuten-csv-upload', 'contents'),
    State('rakuten-csv-upload', 'filename'),
    prevent_initial_call=True,
)
def check_csv(contents, filename):
    if not contents:
        return dash.no_update

    try:
        _content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        csv_df = pd.read_csv(io.StringIO(decoded))
    except Exception as e:
        return dbc.Alert(f"CSVの読み込みに失敗しました: {e}", color="danger")

    if not CSV_REQUIRED_COLUMNS.issubset(csv_df.columns):
        return dbc.Alert(
            "CSVの形式が想定と異なります（利用日・利用店名・商品名・利用金額の列が必要です）。",
            color="danger",
        )

    csv_df = csv_df[list(CSV_REQUIRED_COLUMNS)].copy()
    csv_df['利用金額'] = pd.to_numeric(csv_df['利用金額'], errors='coerce')
    csv_df['利用日'] = pd.to_datetime(csv_df['利用日'], errors='coerce')
    csv_df = csv_df.dropna(subset=['利用日', '利用金額'])
    csv_df['利用金額'] = csv_df['利用金額'].astype(int)
    csv_df['利用日'] = csv_df['利用日'].dt.strftime('%Y-%m-%d')

    if csv_df.empty:
        return dbc.Alert("CSVに有効な明細行がありませんでした。", color="warning")

    date_min, date_max = csv_df['利用日'].min(), csv_df['利用日'].max()

    app_df = fetch_rakuten_data()
    app_df = app_df[(app_df['date'] >= date_min) & (app_df['date'] <= date_max)]
    app_counter = Counter(zip(app_df['date'], app_df['expense'].astype(int)))

    missing_rows = []
    for _, row in csv_df.iterrows():
        key = (row['利用日'], int(row['利用金額']))
        if app_counter[key] > 0:
            app_counter[key] -= 1
        else:
            missing_rows.append(row)

    total = len(csv_df)
    missing_count = len(missing_rows)

    if missing_count == 0:
        return dbc.Alert(f"✅ CSV {total}件すべて家計簿に登録済みでした（{date_min} 〜 {date_max}）。", color="success")

    summary = dbc.Alert(
        f"⚠️ CSV {total}件中 {missing_count}件が家計簿に見つかりませんでした（{date_min} 〜 {date_max}）。"
        "以下の明細が未登録の可能性があります。",
        color="warning",
    )
    missing_df = pd.DataFrame(missing_rows)[['利用日', '利用店名・商品名', '利用金額']]
    missing_df['利用金額'] = missing_df['利用金額'].apply(format_yen_jp)
    table = dbc.Table.from_dataframe(missing_df, striped=True, bordered=True, hover=True, responsive=True)

    return html.Div([summary, table])
