import dash
from dash import html, callback, Output, Input, State, dash_table, dcc
import pandas as pd
import dash_bootstrap_components as dbc
from db.crud import fetch_all_records, delete_record, update_record

dash.register_page(__name__)


def fetch_data():
    data = fetch_all_records('shared_kakeibo_view')
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=['date', 'income', 'expense', 'item', 'category', 'shop', 'payment', 'note', 'created_at', 'editor'])


# マスタデータ取得（名前→IDの逆引きマップも作成）
category_db = fetch_all_records('shared_kakeibo_category')
category_options = [{'label': c['item'], 'value': c['id']} for c in category_db]
category_name_to_id = {c['item']: c['id'] for c in category_db}

shop_db = fetch_all_records('shared_kakeibo_shop')
shop_options = [{'label': s['item'], 'value': s['id']} for s in shop_db]
shop_name_to_id = {s['item']: s['id'] for s in shop_db}

payment_db = fetch_all_records('shared_kakeibo_payment')
payment_options = [{'label': p['item'], 'value': p['id']} for p in payment_db]
payment_name_to_id = {p['item']: p['id'] for p in payment_db}


# 編集モーダル
edit_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("レコード編集")),
    dbc.ModalBody([
        dbc.Form([
            dbc.Row([
                dbc.Label('日付', width=3),
                dbc.Col(dcc.DatePickerSingle(
                    id='edit-date',
                    display_format='YYYY/MM/DD',
                    className='dbc'
                ), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('収入', width=3),
                dbc.Col(dbc.Input(id='edit-income', type='number', min=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('支出', width=3),
                dbc.Col(dbc.Input(id='edit-expense', type='number', min=0), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('品目', width=3),
                dbc.Col(dbc.Input(id='edit-item', type='text', maxLength=100), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('カテゴリ', width=3),
                dbc.Col(dcc.Dropdown(id='edit-category', options=category_options, className='dbc'), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('店名', width=3),
                dbc.Col(dcc.Dropdown(id='edit-shop', options=shop_options, className='dbc'), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('支払方法', width=3),
                dbc.Col(dcc.Dropdown(id='edit-payment', options=payment_options, className='dbc'), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('備考', width=3),
                dbc.Col(dbc.Input(id='edit-note', type='text', maxLength=200), width=9)
            ], className="mb-2"),
            dbc.Row([
                dbc.Label('担当者', width=3),
                dbc.Col(dbc.RadioItems(
                    id='edit-editor',
                    options=[
                        {'label': 'Yuki', 'value': 'Yuki'},
                        {'label': 'Ryoko', 'value': 'Ryoko'}
                    ],
                    inline=True,
                ), width=9)
            ], className="mb-2"),
        ])
    ]),
    dbc.ModalFooter([
        dbc.Alert(id='edit-error-msg', color='danger', is_open=False, className="me-auto py-1 mb-0"),
        dbc.Button("キャンセル", id="cancel-edit-btn", color="secondary", className="me-2"),
        dbc.Button("保存", id="save-edit-btn", color="primary"),
    ]),
], id="edit-modal", is_open=False, size="lg")

# 削除確認モーダル
delete_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("削除確認")),
    dbc.ModalBody("本当に削除しますか?"),
    dbc.ModalFooter([
        dbc.Button("キャンセル", id="cancel-modal-btn", className="ms-auto", n_clicks=0),
        dbc.Button("削除", id="delete-modal-btn", color="danger", n_clicks=0)
    ]),
], id="modal", is_open=False)


layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("データ一覧"), width=6),
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button("更新", id="refresh-btn", color="primary"),
                dbc.Button("編集", id="edit-btn", color="warning", disabled=True),
                dbc.Button("削除", id="delete-btn", color="danger", disabled=True),
            ], size="sm", className="d-flex justify-content-end"),
            width=6,
            className="text-end"
        )
    ], className="mt-3 mb-2"),
    edit_modal,
    delete_modal,
    dbc.Row(
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("選択された行ID"),
                dbc.Input(placeholder="ID", id='selected-row', readonly=True)
            ]),
        ),
        className="mb-2"
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(id='datatable-container', className="dbc dbc-row-selectable")
    ])
], fluid=True)


@callback(
    Output('datatable-container', 'children'),
    Input('refresh-btn', 'n_clicks')
)
def update_table(n_clicks):
    df = fetch_data()
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns if i != 'id'],
        id='datatable',
        row_id_column='id',
        filter_action='native',
        sort_action='native',
        page_action='native',
        row_selectable='single',
        selected_rows=[],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={'textAlign': 'left'},
    )


@callback(
    Output('selected-row', 'value'),
    Output('edit-btn', 'disabled'),
    Output('delete-btn', 'disabled'),
    Input('datatable', 'selected_row_ids')
)
def on_row_selected(selected_row_ids):
    if selected_row_ids:
        return selected_row_ids[0], False, False
    return None, True, True


# 編集モーダルを開き、選択行の値を事前入力
@callback(
    Output('edit-modal', 'is_open'),
    Output('edit-date', 'date'),
    Output('edit-income', 'value'),
    Output('edit-expense', 'value'),
    Output('edit-item', 'value'),
    Output('edit-category', 'value'),
    Output('edit-shop', 'value'),
    Output('edit-payment', 'value'),
    Output('edit-note', 'value'),
    Output('edit-editor', 'value'),
    Output('edit-error-msg', 'is_open'),
    Input('edit-btn', 'n_clicks'),
    Input('cancel-edit-btn', 'n_clicks'),
    State('datatable', 'selected_row_ids'),
    State('datatable', 'data'),
    State('edit-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_edit_modal(edit_clicks, cancel_clicks, selected_row_ids, table_data, is_open):
    triggered = dash.ctx.triggered_id

    if triggered == 'cancel-edit-btn':
        return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False

    if triggered == 'edit-btn' and selected_row_ids:
        row_id = selected_row_ids[0]
        row = next((r for r in table_data if r.get('id') == row_id), None)
        if row is None:
            return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False

        return (
            True,
            row.get('date'),
            row.get('income'),
            row.get('expense'),
            row.get('item'),
            category_name_to_id.get(row.get('category')),
            shop_name_to_id.get(row.get('shop')),
            payment_name_to_id.get(row.get('payment')),
            row.get('note'),
            row.get('editor'),
            False,
        )

    return is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False


# 保存処理
@callback(
    Output('edit-modal', 'is_open', allow_duplicate=True),
    Output('datatable', 'data', allow_duplicate=True),
    Output('edit-error-msg', 'is_open', allow_duplicate=True),
    Output('edit-error-msg', 'children'),
    Input('save-edit-btn', 'n_clicks'),
    State('datatable', 'selected_row_ids'),
    State('edit-date', 'date'),
    State('edit-income', 'value'),
    State('edit-expense', 'value'),
    State('edit-item', 'value'),
    State('edit-category', 'value'),
    State('edit-shop', 'value'),
    State('edit-payment', 'value'),
    State('edit-note', 'value'),
    State('edit-editor', 'value'),
    prevent_initial_call=True
)
def save_edit(n_clicks, selected_row_ids, date, income, expense, item, category, shop, payment, note, editor):
    if not n_clicks or not selected_row_ids:
        return dash.no_update, dash.no_update, dash.no_update, ""

    if not date:
        return dash.no_update, dash.no_update, True, "日付を入力してください。"
    if income is None and expense is None:
        return dash.no_update, dash.no_update, True, "収入または支出を入力してください。"

    row_id = selected_row_ids[0]
    updates = {
        'date': date,
        'income': income,
        'expense': expense,
        'item': item,
        'category': category,
        'shop': shop,
        'payment': payment,
        'note': note,
        'editor': editor,
    }
    # None値は送らない
    updates = {k: v for k, v in updates.items() if v is not None}

    try:
        update_record('shared_kakeibo', row_id, updates)
        return False, fetch_data().to_dict('records'), False, ""
    except Exception:
        return dash.no_update, dash.no_update, True, "保存中にエラーが発生しました。"


# 削除モーダル開閉
@callback(
    Output('modal', 'is_open'),
    Input('delete-btn', 'n_clicks'),
    Input('cancel-modal-btn', 'n_clicks'),
    Input('delete-modal-btn', 'n_clicks'),
    State('modal', 'is_open')
)
def toggle_delete_modal(delete_clicks, close_clicks, delete_modal_clicks, is_open):
    triggered = dash.ctx.triggered_id
    if triggered in ('delete-btn', 'cancel-modal-btn', 'delete-modal-btn'):
        return not is_open
    return is_open


# 削除処理
@callback(
    Output('datatable', 'data'),
    Output('datatable', 'selected_row_ids'),
    Input('delete-modal-btn', 'n_clicks'),
    State('datatable', 'selected_row_ids')
)
def delete_selected_row(n_clicks, selected_row_ids):
    if (n_clicks or 0) > 0 and selected_row_ids:
        row_id = selected_row_ids[0]
        if not isinstance(row_id, int) or row_id <= 0:
            return dash.no_update, dash.no_update
        try:
            delete_record('shared_kakeibo', row_id)
        except Exception:
            return dash.no_update, dash.no_update
        return fetch_data().to_dict('records'), []
    return dash.no_update, dash.no_update
