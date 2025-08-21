import dash
from dash import html, dcc
from datetime import date
import dash_bootstrap_components as dbc
from db.crud import insert_record, fetch_all_records
from datetime import datetime

dash.register_page(__name__)

category_db = fetch_all_records('shared_kakeibo_category')
category_options = [{'label': category['item'], 'value': category['id']} for category in category_db]

shop_db = fetch_all_records('shared_kakeibo_shop')
shop_options = [{'label': shop['item'], 'value': shop['id']} for shop in shop_db]

payment_db = fetch_all_records('shared_kakeibo_payment')
payment_options = [{'label': payment['item'], 'value': payment['id']} for payment in payment_db]

layout = html.Div([
    html.H1('家計簿入力フォーム'),
    html.P('ドロップダウンに無い場合は、その他を選択して、備考欄に記入してね！追加機能は開発中です！'),
    dbc.Toast(
            "データを追加しました！",
            id="success-toast",
            header="成功",
            is_open=False,
            dismissable=True,
            icon="success",
            duration=4000,  # 4秒後に自動で閉じる
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    ),
    dbc.Form([
        dbc.Row([
            dbc.Label('日付', html_for='date-picker-single', width=2),
            dbc.Col(dcc.DatePickerSingle(
                id='date-picker-single',
                min_date_allowed=date(2021, 4, 1),
                date=date.today(),
                display_format='YYYY/MM/DD',
                className='dbc'
            ), width=10)
        ]),
        dbc.Row([
            dbc.Label('収入', html_for='income-input', width=2),
            dbc.Col(dbc.Input(id='income-input', type='number', placeholder='収入', min=0), width=10)
        ]),
        dbc.Row([
            dbc.Label('支出', html_for='expense-input', width=2),
            dbc.Col(dbc.Input(id='expense-input', type='number', placeholder='支出', min=0), width=10)
        ]),
        dbc.Row([
            dbc.Label('品目', html_for='item-input', width=2),
            dbc.Col(dbc.Input(id='item-input', type='text', placeholder='品目'), width=10)
        ]),
        dbc.Row([
            dbc.Label('カテゴリ', html_for='category-dropdown', width=2),
            dbc.Col(
                dcc.Dropdown(
                    id='category-dropdown',
                    options=category_options,
                    placeholder='カテゴリ',
                    className='dbc'
                    ), 
                width=10
            )
        ]),
        dbc.Row([
            dbc.Label('店名', html_for='shop-dropdown', width=2),
            dbc.Col(dcc.Dropdown(
                id='shop-dropdown',
                options=shop_options,
                placeholder='店名',
                className='dbc'
                ), 
                width=10
            )
        ]),
        dbc.Row([
            dbc.Label('支払方法', html_for='payment-dropdown', width=2),
            dbc.Col(dcc.Dropdown(
                id='payment-dropdown',
                options=payment_options,
                placeholder='支払方法',
                className='dbc'
                ), 
                width=10)
        ]),
        dbc.Row([
            dbc.Label('備考', html_for='remark-input', width=2),
            dbc.Col(dbc.Input(
                id='remark-input',
                type='text',
                placeholder='備考'
            ), width=10)
        ]),
        dbc.Row([
            dbc.Label('担当者', html_for='editor-input', width=2),
            dbc.Col(dbc.RadioItems(
                id='editor-input',
                options=[
                    {'label': 'Yuki', 'value': 'Yuki'},
                    {'label': 'Ryoko', 'value': 'Ryoko'}
                ],
                inline=True,
            ), width=10)
        ])
    ]),
    dbc.Stack(
        [
            dbc.Button('Submit', id='submit-button', n_clicks=0),
            dbc.Button('Reset', id='reset-button', n_clicks=0, color='secondary')
        ],
        direction='horizontal',
        gap=2
    ),
])

@dash.callback(
    dash.Output('submit-button', 'n_clicks'),
    dash.Output('success-toast', 'is_open'),
    [dash.Input('submit-button', 'n_clicks')],
    [
        dash.State('date-picker-single', 'date'),
        dash.State('income-input', 'value'),
        dash.State('expense-input', 'value'),
        dash.State('item-input', 'value'),
        dash.State('category-dropdown', 'value'),
        dash.State('shop-dropdown', 'value'),
        dash.State('payment-dropdown', 'value'),
        dash.State('remark-input', 'value'),
        dash.State('editor-input', 'value')
    ]
)
def insert_data(n_clicks, date_value, income_value, expense_value, item_value, category_value, shop_value, payment_value, remark_value, editor_value):
    if n_clicks > 0:
        record = {
            'date': date_value,
            'income': income_value,
            'expense': expense_value,
            'item': item_value,
            'category': category_value,
            'shop': shop_value,
            'payment': payment_value,
            'note': remark_value,
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'editor': editor_value
        }
        insert_record('shared_kakeibo', record)
        return n_clicks + 1, True
    return 0, False

@dash.callback(
    dash.Output('date-picker-single', 'date'),
    dash.Output('income-input', 'value'),
    dash.Output('expense-input', 'value'),
    dash.Output('item-input', 'value'),
    dash.Output('category-dropdown', 'value'),
    dash.Output('shop-dropdown', 'value'),
    dash.Output('payment-dropdown', 'value'),
    dash.Output('remark-input', 'value'),
    [dash.Input('reset-button', 'n_clicks')]
)
def reset_form(n_clicks):
    return (
        date.today().isoformat(),  # Reset date to today
        None,  # Reset income
        None,  # Reset expense
        '',    # Reset item
        None,  # Reset category
        None,  # Reset shop
        None,  # Reset payment
        ''     # Reset remark
    )
