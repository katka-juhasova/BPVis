import dash_core_components as dcc
import plotly.graph_objects as go


def get_empty_figure():
    fig = {
        'data': [],
        'layout': go.Layout(
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


def get_colorful_figure():
    fig = {
        'data': [],
        'layout': go.Layout(
            xaxis={
                'showticklabels': False,
                'ticks': '',
                'zeroline': False
            },
            yaxis={
                'showticklabels': False,
                'ticks': '',
                'zeroline': False
            }
        )
    }

    return fig
