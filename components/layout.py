"""
Module containing placeholder components and a component for inclusion of
static legend.
"""

import plotly.graph_objects as go
import dash_html_components as html
import base64


def get_empty_figure(height: int):
    """
    Creates empty grey placeholder component which shall be later substituted
    with diagram. The given height determines the height of the placeholder.

    Parameters
    ----------
    height : int
        height of placeholder in pixels

    Returns
    -------
    go.Figure
        object representing empty grey placeholder
    """

    fig = {
        'data': [],
        'layout': go.Layout(
            height=height,
            paper_bgcolor='#eaeaea',
            plot_bgcolor='#eaeaea',
            xaxis={
                'showticklabels': False,
                'ticks': '',
                'showgrid': False,
                'zeroline': False
            },
            yaxis={
                'showticklabels': False,
                'ticks': '',
                'showgrid': False,
                'zeroline': False
            }
        )
    }

    return fig


def get_empty_div(height: int):
    """
    Creates empty grey placeholder component which shall be later substituted
    with div. The given height determines the height of the placeholder.

    Parameters
    ----------
    height : int
        height of placeholder in pixels

    Returns
    -------
    html.Div
        object representing empty grey placeholder
    """

    return html.Div(
        [],
        style={
            'height': height,
            'margin-top': '10px',
            'margin-bottom': '10px',
            'background-color': '#eaeaea'
        }
    )


def get_legend_image():
    """
    Loads the image of legend and processes it so that it can be used in
    html.Img component.

    Returns
    -------
    str
        encoded binary representation of legend image
    """

    with open('assets/legend.png', 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    encoded_image = 'data:image/png;base64,' + encoded_string

    return encoded_image
