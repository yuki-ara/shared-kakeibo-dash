from datetime import datetime
import pandas as pd
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import plotly.graph_objects as go
from db.crud import fetch_all_records

dash.register_page(__name__)

# 突発的・特別支出として通常グラフから除外するカテゴリ
IRREGULAR_CATEGORIES = ['家具・家電', '交際費', '旅行費', '冠婚葬祭', 'その他']

# 通常カテゴリの月間予算（毎月固定額）。金額を変更する場合はコードを編集してサービスを再起動してください。
# 交通費・通信費・医療費・教育費は未設定（0円）
BUDGETS = {
    '電気代':   9000,
    'ガス代':   5000,
    '水道代':   8000,
    '食費':    27000,
    '外食':    13000,
    '日用品':   10000,
    'サブスク':  2000,
    '娯楽費':   3000,
    '交通費':      0,
    '通信費':      0,
    '医療費':      0,
    '教育費':      0,
}

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

def build_budget_summary_card(actual_by_category):
    total_budget = sum(b for b in BUDGETS.values() if b > 0)
    total_actual = sum(actual_by_category.get(cat, 0) for cat, b in BUDGETS.items() if b > 0)
    diff = total_actual - total_budget
    if diff > 0:
        diff_label, diff_class = f"{format_yen_jp(diff)}オーバー", "text-danger"
    else:
        diff_label, diff_class = f"{format_yen_jp(-diff)}余裕", "text-success"
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("予算合計"),
            dbc.CardBody(html.H5(format_yen_jp(total_budget), className="mb-0")),
        ]), width=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader("予算に対する過不足"),
            dbc.CardBody(html.H5(diff_label, className=f"mb-0 fw-bold {diff_class}")),
        ]), width=6),
    ], className="g-2 mb-3")

def build_budget_progress(actual_by_category):
    rows = []
    for category, budget in BUDGETS.items():
        actual = actual_by_category.get(category, 0)
        if budget <= 0:
            rows.append(dbc.Row([
                dbc.Col(html.Span(category, className="fw-bold"), width=4, md=3),
                dbc.Col(dbc.Progress(value=0, color='secondary', style={"height": "20px"}), width=5, md=6),
                dbc.Col(html.Span(f"{format_yen_jp(actual)}（予算未設定）", className="small text-muted"), width=3),
            ], className="mb-2 align-items-center"))
            continue
        pct = actual / budget * 100
        color = 'danger' if pct >= 100 else 'warning' if pct >= 80 else 'success'
        amount_class = "small text-danger fw-bold" if pct >= 100 else "small text-muted"
        rows.append(dbc.Row([
            dbc.Col(html.Span(category, className="fw-bold"), width=4, md=3),
            dbc.Col(dbc.Progress(value=min(pct, 100), color=color, label=f"{pct:.0f}%", style={"height": "20px"}), width=5, md=6),
            dbc.Col(html.Span(f"{format_yen_jp(actual)} / {format_yen_jp(budget)}", className=amount_class), width=3),
        ], className="mb-2 align-items-center"))
    return html.Div(rows)

def build_month_cards(income, expense, balance):
    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("収入"), dbc.CardBody(html.H5(f"{format_yen_jp(income)}", className="mb-0"))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("支出"), dbc.CardBody(html.H5(f"{format_yen_jp(expense)}", className="mb-0"))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("収支"), dbc.CardBody(html.H5(f"{format_yen_jp(balance)}", className="mb-0" + (" text-danger" if balance < 0 else "")))]), width=4),
    ], className="g-2 mb-3")

def fetch_data():
    data = fetch_all_records('shared_kakeibo_view')
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=['date', 'income', 'expense', 'item', 'category', 'shop', 'payment', 'note', 'created_at', 'editor'])

load_figure_template('minty')


total_income_card = dbc.Card([
    dbc.CardHeader("総収入"),
    dbc.CardBody([
        html.H4("計算中...", className="card-title", id="total-income"),
    ]),
])
total_expense_card = dbc.Card([
    dbc.CardHeader("総支出"),
    dbc.CardBody([
        html.H4("計算中...", className="card-title", id="total-expense"),
    ]),
])
total_balance_card = dbc.Card([
    dbc.CardHeader("総残額"),
    dbc.CardBody([
        html.H4("計算中...", className="card-title", id="total-balance"),
    ]),
])
total_balance_ratio_card = dbc.Card([
    dbc.CardHeader("総残額比率"),
    dbc.CardBody([
        html.H4("計算中...", className="card-title", id="total-balance-ratio"),
    ]),
])

# balance_ratio_gauge = go.Figure(go.Indicator(
#     mode="gauge+number",
#     value=23.12,
#     title={"text": "総残額比率"},
#     gauge={
#         'axis': {'range': [None, 100]},
#         'bar': {'color': "darkblue"},
#         # 'steps': [
#         #     {'range': [0, 50], 'color': "lightgray"},
#         #     {'range': [50, 100], 'color': "lightgreen"},
#         # ],
#         'threshold': {
#             'line': {'color': "red", 'width': 4},
#             'thickness': 0.75,
#             'value': 100
#         }
#     }
# ))

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("家計簿データ分析ダッシュボード"), width=12, className="text-center mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("更新", id='refresh-data-button', color='primary', className="mb-4"), width=2)
    ]),
    dbc.Row([
        dbc.Col(total_income_card,        width=12, md=3),
        dbc.Col(total_expense_card,       width=12, md=3),
        dbc.Col(total_balance_card,       width=12, md=3),
        dbc.Col(total_balance_ratio_card, width=12, md=3),
    ], className="g-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='pie-expense-category'),       width=12, md=4, className="mb-4"),
        dbc.Col(dcc.Graph(id='income-outcome-trend-graph'), width=12, md=8, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("突発・特別支出", className="mb-3 text-muted"),
            html.Div(id='irregular-expense-cards'),
        ], width=12, md=6, className="mb-4"),
        dbc.Col(dcc.Graph(id='saving-rate-graph'), width=12, md=6, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='area-income-outcome-trend'), width=12, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("月別サマリー", className="mb-3 text-muted"),
            dcc.Dropdown(id='month-selector', clearable=False, className="dbc mb-3", style={"maxWidth": "220px"}),
            html.Div(id='month-summary-cards'),
            html.Div(id='budget-summary-cards'),
            html.Div(id='budget-progress-list'),
        ], width=12, className="mb-4"),
    ]),
    dbc.Row([
        dbc.Col(id='table-monthly-summary', width=12, className="mb-4"),
    ]),
    dcc.Store(id='monthly-data-store'),
], fluid=True)

@callback(
    [
        Output('total-income', 'children'),
        Output('total-expense', 'children'),
        Output('total-balance', 'children'),
        Output('total-balance-ratio', 'children'),
        Output('pie-expense-category', 'figure'),
        Output('income-outcome-trend-graph', 'figure'),
        Output('irregular-expense-cards', 'children'),
        Output('saving-rate-graph', 'figure'),
        Output('area-income-outcome-trend', 'figure'),
        Output('table-monthly-summary', 'children'),
        Output('month-selector', 'options'),
        Output('month-selector', 'value'),
        Output('monthly-data-store', 'data'),
    ],
    Input('refresh-data-button', 'n_clicks')
)
def update_income_outcome_trend(n_clicks):
    df = fetch_data()
    df['YearMonth'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)

    # Value for Cards
    total_income        = df['income'].sum()
    total_expense       = df['expense'].sum()
    total_balance       = total_income - total_expense
    total_balance_ratio = (total_balance / total_income * 100) if total_income != 0 else 0

    # Graphs
    df_regular   = df[~df['category'].isin(IRREGULAR_CATEGORIES)]
    df_irregular = df[ df['category'].isin(IRREGULAR_CATEGORIES)]

    df_grouped_regular  = df_regular.groupby(['YearMonth', 'category'], as_index=False).sum()
    df_grouped_irregular= df_irregular.groupby(['YearMonth', 'category'], as_index=False).sum()
    df_grouped_regular['expense_label'] = df_grouped_regular['expense'].apply(format_yen_jp)

    ## Pie Chart by Category (通常支出のみ)
    pie_fig = px.pie(
        df_grouped_regular,
        names='category',
        values='expense',
        title='支出カテゴリ別割合（通常支出）',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        custom_data=['expense_label'],
    )
    pie_fig.update_traces(hovertemplate='%{label}<br>%{customdata[0]}<br>%{percent}<extra></extra>')

    ## Bar Chart by Category and Month (通常支出のみ)
    bar_fig = px.bar(
        df_grouped_regular,
        x='YearMonth',
        y='expense',
        color='category',
        barmode='stack',
        text='expense_label',
        title='月ごとの支出カテゴリ別集計（通常支出）',
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    bar_fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{text}<extra></extra>')

    ## Cards for Irregular Expenses
    if df_grouped_irregular.empty:
        irregular_cards = html.P("該当データなし", className="text-muted")
    else:
        df_irr_month = df_grouped_irregular.groupby('YearMonth')
        cards = []
        for ym, group in df_irr_month:
            total = group['expense'].sum()
            breakdown = [
                html.Li(f"{row['category']}: {format_yen_jp(row['expense'])}", className="small")
                for _, row in group.iterrows() if row['expense'] > 0
            ]
            cards.append(
                dbc.Card([
                    dbc.CardHeader(ym, className="py-1 px-2 small fw-bold"),
                    dbc.CardBody([
                        html.P(f"合計: {format_yen_jp(total)}", className="mb-1 fw-bold"),
                        html.Ul(breakdown, className="mb-0 ps-3"),
                    ], className="py-2 px-2"),
                ], className="mb-2", style={"fontSize": "0.85rem"})
            )
        irregular_cards = html.Div(cards, style={"maxHeight": "400px", "overflowY": "auto"})

    ## Monthly Summary (貯蓄率グラフ・エリアチャート共通データ)
    df['balance'] = df['income'].fillna(0) - df['expense'].fillna(0)
    df_monthly_summary = df.groupby('YearMonth').agg(
        monthly_income =('income', 'sum'),
        monthly_expense=('expense', 'sum'),
        monthly_balance=('balance', 'sum')
    ).reset_index()
    df_monthly_summary['total_saving'] = df_monthly_summary['monthly_balance'].cumsum()
    df_monthly_summary['saving_rate']  = (df_monthly_summary['monthly_balance'] / df_monthly_summary['monthly_income'].replace(0, float('nan')) * 100).fillna(0)

    ## Saving Rate Line Chart
    saving_rate_fig = go.Figure(go.Scatter(
        x=df_monthly_summary['YearMonth'],
        y=df_monthly_summary['saving_rate'],
        mode='lines+markers+text',
        line=dict(color='#636efa', width=2),
        marker=dict(size=7),
        text=[f"{v:.1f}%" for v in df_monthly_summary['saving_rate']],
        textposition='top center',
    ))
    saving_rate_fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
    saving_rate_fig.update_layout(
        title='月次貯蓄率',
        xaxis_title='年月',
        yaxis_title='貯蓄率（%）',
        yaxis=dict(ticksuffix='%'),
        showlegend=False,
    )

    ## Area Chart for Income and Expense Trend
    area_hovertemplate = '%{x}<br>%{fullData.name}: %{text}<extra></extra>'
    area_fig = go.Figure()
    area_fig.add_trace(go.Scatter(
        x=df_monthly_summary['YearMonth'], y=df_monthly_summary['monthly_income'], name='月収入',
        mode='lines+markers', line_shape='spline', fill='tozeroy',
        text=df_monthly_summary['monthly_income'].apply(format_yen_jp), hovertemplate=area_hovertemplate,
    ))
    area_fig.add_trace(go.Scatter(
        x=df_monthly_summary['YearMonth'], y=df_monthly_summary['monthly_expense'], name='月支出',
        mode='lines+markers', line_shape='spline', fill='tozeroy',
        text=df_monthly_summary['monthly_expense'].apply(format_yen_jp), hovertemplate=area_hovertemplate,
    ))
    area_fig.add_trace(go.Scatter(
        x=df_monthly_summary['YearMonth'], y=df_monthly_summary['total_saving'], name='総貯蓄額',
        mode='lines+markers', line_shape='spline', line_color='blue',
        text=df_monthly_summary['total_saving'].apply(format_yen_jp), hovertemplate=area_hovertemplate,
    ))
    area_fig.update_layout(title='収入と支出の月ごとの推移', xaxis_title='年月', yaxis_title='金額')
    area_fig.update_xaxes(tickmode='array', tickvals=df_monthly_summary['YearMonth'], ticktext=df_monthly_summary['YearMonth'])

    ## Table for Monthly Summary
    table_monthly_summary = dbc.Table.from_dataframe(
        df_monthly_summary,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )

    ## Month Selector (現在の月をデフォルト選択、データが無い月でも選べるようにする)
    current_month = datetime.now().strftime('%Y-%m')
    available_months = set(df['YearMonth'].unique()) if not df.empty else set()
    available_months.add(current_month)
    month_options = [{'label': m, 'value': m} for m in sorted(available_months, reverse=True)]

    monthly_data = {
        'grouped_regular': df_grouped_regular[['YearMonth', 'category', 'expense']].to_dict('records'),
        'monthly_summary': df_monthly_summary[['YearMonth', 'monthly_income', 'monthly_expense', 'monthly_balance']].to_dict('records'),
    }

    return (
        f"{format_yen_jp(total_income)}",
        f"{format_yen_jp(total_expense)}",
        f"{format_yen_jp(total_balance)}",
        f"{total_balance_ratio:.2f}%",
        pie_fig,
        bar_fig,
        irregular_cards,
        saving_rate_fig,
        area_fig,
        table_monthly_summary,
        month_options,
        current_month,
        monthly_data,
    )


@callback(
    Output('month-summary-cards', 'children'),
    Output('budget-summary-cards', 'children'),
    Output('budget-progress-list', 'children'),
    Input('month-selector', 'value'),
    State('monthly-data-store', 'data'),
)
def update_month_summary(selected_month, monthly_data):
    if not selected_month or not monthly_data:
        empty = html.P("データがありません", className="text-muted")
        return empty, empty, empty

    monthly_summary = pd.DataFrame(monthly_data.get('monthly_summary', []))
    grouped_regular = pd.DataFrame(monthly_data.get('grouped_regular', []))

    if not monthly_summary.empty and selected_month in monthly_summary['YearMonth'].values:
        row = monthly_summary[monthly_summary['YearMonth'] == selected_month].iloc[0]
        income, expense, balance = row['monthly_income'], row['monthly_expense'], row['monthly_balance']
    else:
        income = expense = balance = 0

    month_cards = build_month_cards(income, expense, balance)

    if not grouped_regular.empty and selected_month in grouped_regular['YearMonth'].values:
        actual_by_category = (
            grouped_regular[grouped_regular['YearMonth'] == selected_month]
            .set_index('category')['expense']
            .to_dict()
        )
    else:
        actual_by_category = {}

    return month_cards, build_budget_summary_card(actual_by_category), build_budget_progress(actual_by_category)

