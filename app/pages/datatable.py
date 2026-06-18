import dash
from dash import html, callback, Output, Input, State, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
from db.crud import fetch_all_records, delete_record

dash.register_page(__name__)

# Fetch data from the database
def fetch_data():
    data = fetch_all_records('shared_kakeibo_view')
    if data:
        return pd.DataFrame(data)
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
    [Output('datatable', 'data'), Output('datatable', 'selected_row_ids')],
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