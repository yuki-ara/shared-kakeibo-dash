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
        dbc.Col(id='table-monthly-summary', width=12, className="mb-4"),
    ]),
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
        Output('table-monthly-summary', 'children')
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

    ## Pie Chart by Category (通常支出のみ)
    pie_fig = px.pie(
        df_grouped_regular,
        names='category',
        values='expense',
        title='支出カテゴリ別割合（通常支出）',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    ## Bar Chart by Category and Month (通常支出のみ)
    bar_fig = px.bar(
        df_grouped_regular,
        x='YearMonth',
        y='expense',
        color='category',
        barmode='stack',
        text_auto=True,
        title='月ごとの支出カテゴリ別集計（通常支出）',
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    ## Cards for Irregular Expenses
    if df_grouped_irregular.empty:
        irregular_cards = html.P("該当データなし", className="text-muted")
    else:
        df_irr_month = df_grouped_irregular.groupby('YearMonth')
        cards = []
        for ym, group in df_irr_month:
            total = group['expense'].sum()
            breakdown = [
                html.Li(f"{row['category']}: {row['expense']:,.0f}円", className="small")
                for _, row in group.iterrows() if row['expense'] > 0
            ]
            cards.append(
                dbc.Card([
                    dbc.CardHeader(ym, className="py-1 px-2 small fw-bold"),
                    dbc.CardBody([
                        html.P(f"合計: {total:,.0f}円", className="mb-1 fw-bold"),
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
    area_fig = go.Figure()
    area_fig.add_trace(go.Scatter(x=df_monthly_summary['YearMonth'], y=df_monthly_summary['monthly_income'] , name='月収入', mode='lines+markers', line_shape='spline', fill='tozeroy'))
    area_fig.add_trace(go.Scatter(x=df_monthly_summary['YearMonth'], y=df_monthly_summary['monthly_expense'], name='月支出', mode='lines+markers', line_shape='spline', fill='tozeroy'))
    area_fig.add_trace(go.Scatter(x=df_monthly_summary['YearMonth'], y=df_monthly_summary['total_saving'], name='総貯蓄額', mode='lines+markers', line_shape='spline', line_color='blue'))
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

    return (
        f"{total_income:,.0f}円",
        f"{total_expense:,.0f}円",
        f"{total_balance:,.0f}円",
        f"{total_balance_ratio:.2f}%",
        pie_fig,
        bar_fig,
        irregular_cards,
        saving_rate_fig,
        area_fig,
        table_monthly_summary,
    )

