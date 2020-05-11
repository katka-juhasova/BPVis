import plotly.graph_objects as go
import dash_html_components as html


def get_empty_figure(height: int):
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
    return html.Div([],
                    style={'height': height,
                           'margin-top': '10px',
                           'margin-bottom': '10px',
                           'background-color': '#eaeaea'})
