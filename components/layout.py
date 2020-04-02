import dash_html_components as html
from constant import COLUMNS


def blank_column(columns: str):
    return html.Pre(
        children='',
        className=COLUMNS[columns]
    )
