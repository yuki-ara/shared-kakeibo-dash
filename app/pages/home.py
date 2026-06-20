import dash
from dash import html

dash.register_page(__name__, path='/')


layout = html.Div([
    html.H1('共同家計簿アプリへようこそ！'),
    html.Div('右上のメニューから選んでね。'),
    html.Ul([
        html.Li("楽天カードで支払ったものは入力不要。毎月12日に明細が確定後、まとめてアップロードします。"),
        html.Li("それ以外で支払ったものは、各自で入力すること。"),
        html.Li("ｳﾗｳﾗﾔﾊﾔﾊ"),
    ]),
    html.Div(
        html.Img(
            src='assets/chiikawa-usagi.png',
            style={'maxWidth': '100%', 'height': 'auto', 'display': 'block'}
        ),
        style={'marginTop': '16px'}
    )
])