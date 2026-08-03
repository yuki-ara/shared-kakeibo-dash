import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
from db.crud import fetch_all_records, delete_record, fetch_record_by_id, update_record

dash.register_page(__name__)

category_options = [{'label': c['item'], 'value': c['id']} for c in fetch_all_records('shared_kakeibo_category')]
shop_options = [{'label': s['item'], 'value': s['id']} for s in fetch_all_records('shared_kakeibo_shop')]
payment_options = [{'label': p['item'], 'value': p['id']} for p in fetch_all_records('shared_kakeibo_payment')]


def fetch_data():
    data = fetch_all_records('shared_kakeibo_view')
    if data:
        df = pd.DataFrame(data)
        return df.sort_values(['date', 'created_at'], ascending=False, ignore_index=True)
    else:
        return pd.DataFrame(columns=['date', 'income', 'expense', 'item', 'category', 'shop', 'payment', 'note', 'created_at', 'editor'])


layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("データ一覧"), width=6),
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button("更新", id="refresh-btn", color="primary", className="me-2"),
                dbc.Button("編集", id="edit-btn", color="warning", className="me-2", disabled=True),
                dbc.Button("削除", id="delete-btn", color="danger"),
            ], size="sm", className="d-flex justify-content-end"),
            width=6,
            className="text-end"
        )
    ], className="mt-3"),
    dbc.Toast(
        "データを更新しました！",
        id="edit-success-toast",
        header="成功",
        is_open=False,
        dismissable=True,
        icon="success",
        duration=4000,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    ),
    dbc.Toast(
        "データを削除しました！",
        id="delete-success-toast",
        header="成功",
        is_open=False,
        dismissable=True,
        icon="success",
        duration=4000,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("削除確認")),
            dbc.ModalBody("本当に削除しますか?"),
            dbc.ModalFooter(
                [
                    dbc.Button("Cancel", id="cancel-modal-btn", className="ms-auto", n_clicks=0),
                    dbc.Button("Delete", id="delete-modal-btn", color="danger", n_clicks=0)
                ]
            ),
        ],
        id="modal",
        is_open=False,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("レコード編集")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Label('日付', html_for='edit-date', width=3),
                        dbc.Col(dcc.DatePickerSingle(
                            id='edit-date',
                            display_format='YYYY/MM/DD',
                            className='dbc'
                        ), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('収入', html_for='edit-income', width=3),
                        dbc.Col(dbc.Input(id='edit-income', type='number'), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('支出', html_for='edit-expense', width=3),
                        dbc.Col(dbc.Input(id='edit-expense', type='number'), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('品目', html_for='edit-item', width=3),
                        dbc.Col(dbc.Input(id='edit-item', type='text', maxLength=100), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('カテゴリ', html_for='edit-category', width=3),
                        dbc.Col(dcc.Dropdown(
                            id='edit-category',
                            options=category_options,
                            className='dbc'
                        ), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('店名', html_for='edit-shop', width=3),
                        dbc.Col(dcc.Dropdown(
                            id='edit-shop',
                            options=shop_options,
                            className='dbc'
                        ), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('支払方法', html_for='edit-payment', width=3),
                        dbc.Col(dcc.Dropdown(
                            id='edit-payment',
                            options=payment_options,
                            className='dbc'
                        ), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('備考', html_for='edit-note', width=3),
                        dbc.Col(dbc.Input(id='edit-note', type='text', maxLength=200), width=9)
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Label('担当者', html_for='edit-editor', width=3),
                        dbc.Col(dbc.RadioItems(
                            id='edit-editor',
                            options=[
                                {'label': 'Yuki', 'value': 'Yuki'},
                                {'label': 'Ryoko', 'value': 'Ryoko'}
                            ],
                            inline=True,
                        ), width=9)
                    ], className="mb-2"),
                    dbc.Alert(id='edit-error-msg', color='danger', is_open=False, className="mb-0"),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("キャンセル", id="cancel-edit-btn", className="ms-auto", n_clicks=0),
                dbc.Button("保存", id="save-edit-btn", color="warning", n_clicks=0)
            ]),
        ],
        id="edit-modal",
        is_open=False,
    ),
    dbc.Row(
        dbc.Col(
            dbc.InputGroup(
                [dbc.InputGroupText("選択された行ID"), dbc.Input(placeholder="ID", id='selected-row')],
            )
        )
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(id='datatable-container', className="dbc dbc-row-selectable")
    ])
])


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
    Input('datatable', 'selected_row_ids')
)
def show_selected_row_id(selected_row_ids):
    if selected_row_ids:
        return selected_row_ids[0]
    return None


@callback(
    Output('edit-btn', 'disabled'),
    Input('datatable', 'selected_row_ids')
)
def toggle_edit_button(selected_row_ids):
    return not bool(selected_row_ids)


@callback(
    Output('modal', 'is_open'),
    Input('delete-btn', 'n_clicks'),
    Input('cancel-modal-btn', 'n_clicks'),
    Input('delete-modal-btn', 'n_clicks'),
    State('modal', 'is_open')
)
def toggle_modal(delete_clicks, close_clicks, delete_modal_clicks, is_open):
    triggered = dash.ctx.triggered_id
    if triggered in ('delete-btn', 'cancel-modal-btn', 'delete-modal-btn'):
        return not is_open
    return is_open


@callback(
    Output('datatable', 'data'),
    Output('datatable', 'selected_row_ids'),
    Output('delete-success-toast', 'is_open'),
    Input('delete-modal-btn', 'n_clicks'),
    State('datatable', 'selected_row_ids')
)
def delete_selected_row(n_clicks, selected_row_ids):
    if (n_clicks or 0) > 0 and selected_row_ids:
        row_id = selected_row_ids[0]
        if not row_id:
            return dash.no_update, dash.no_update, False
        try:
            delete_record('shared_kakeibo', row_id)
        except Exception:
            return dash.no_update, dash.no_update, False
        return fetch_data().to_dict('records'), [], True
    return dash.no_update, dash.no_update, False


@callback(
    Output('edit-modal', 'is_open'),
    Input('edit-btn', 'n_clicks'),
    Input('cancel-edit-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_edit_modal(edit_clicks, cancel_clicks):
    return dash.ctx.triggered_id == 'edit-btn'


@callback(
    Output('edit-date', 'date'),
    Output('edit-income', 'value'),
    Output('edit-expense', 'value'),
    Output('edit-item', 'value'),
    Output('edit-category', 'options'),
    Output('edit-category', 'value'),
    Output('edit-shop', 'options'),
    Output('edit-shop', 'value'),
    Output('edit-payment', 'options'),
    Output('edit-payment', 'value'),
    Output('edit-note', 'value'),
    Output('edit-editor', 'value'),
    Input('edit-modal', 'is_open'),
    State('selected-row', 'value'),
    prevent_initial_call=True
)
def populate_edit_form(is_open, row_id):
    nu = (dash.no_update,) * 12
    if not is_open or row_id is None:
        return nu
    try:
        records = fetch_record_by_id('shared_kakeibo', row_id)
    except Exception:
        return nu
    if not records:
        return nu
    r = records[0]
    category_opts = [{'label': c['item'], 'value': c['id']} for c in fetch_all_records('shared_kakeibo_category')]
    shop_opts = [{'label': s['item'], 'value': s['id']} for s in fetch_all_records('shared_kakeibo_shop')]
    payment_opts = [{'label': p['item'], 'value': p['id']} for p in fetch_all_records('shared_kakeibo_payment')]
    return (
        r.get('date'), r.get('income'), r.get('expense'), r.get('item'),
        category_opts, r.get('category'),
        shop_opts, r.get('shop'),
        payment_opts, r.get('payment'),
        r.get('note'), r.get('editor')
    )


@callback(
    Output('datatable', 'data', allow_duplicate=True),
    Output('datatable', 'selected_row_ids', allow_duplicate=True),
    Output('edit-modal', 'is_open', allow_duplicate=True),
    Output('edit-error-msg', 'is_open'),
    Output('edit-error-msg', 'children'),
    Output('edit-success-toast', 'is_open'),
    Input('save-edit-btn', 'n_clicks'),
    State('selected-row', 'value'),
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
def save_edit(n_clicks, row_id, date_val, income, expense, item, category, shop, payment, note, editor):
    keep_open = (dash.no_update, dash.no_update, True)

    if not n_clicks or row_id is None:
        return dash.no_update, dash.no_update, dash.no_update, False, "", False
    if not date_val:
        return *keep_open, True, "日付を入力してください。", False
    if not editor:
        return *keep_open, True, "担当者を選択してください。", False
    if income is None and expense is None:
        return *keep_open, True, "収入または支出を入力してください。", False

    updates = {
        'date': date_val,
        'income': income,
        'expense': expense,
        'item': item,
        'category': category,
        'shop': shop,
        'payment': payment,
        'note': note,
        'editor': editor,
    }
    try:
        update_record('shared_kakeibo', row_id, updates)
    except Exception as e:
        print(f"[ERROR] save_edit: {type(e).__name__}: {e}")
        return *keep_open, True, "保存中にエラーが発生しました。しばらくしてから再試行してください。", False

    return fetch_data().to_dict('records'), [], False, False, "", True
