import plotly.graph_objects as go
import dash_html_components as html
import base64


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


def get_legend_image():
    with open('assets/legend.png', 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    encoded_image = 'data:image/png;base64,' + encoded_string

    # encoded_image = base64.b64encode(open('assets/legend.png', 'rb').read()
    # trendImage = 'data:image/png;base64,{}'.format(encoded_image)

    return encoded_image
