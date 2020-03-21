import dash_html_components as html
from src.constant import COLUMNS


def blank_column(columns: str):
    return html.Div(
        children='x',
        style={
            'color': 'white'
        },
        className=COLUMNS[columns]
    )
