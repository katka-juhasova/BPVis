import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from sample import Sample
from components.luacode import LuaCode
from components.seesoft import SeeSoft
from components.scatterplot import ScatterPlot
from components.tree import Tree
from components.clusters import Clusters
# from constant import COLORS
# from constant import LUA_LINE_HEIGHT
from dash.dependencies import Input, Output, State

DIMENSIONS = 7
here = os.path.dirname(os.path.realpath(__file__))

# path = os.path.dirname(os.path.realpath(__file__)) + '/test_data'
# files = list()
#
# # r=root, d=directories, f=files
# # list all json files
# for r, d, f in os.walk(path):
#     for file in f:
#         if '.json' in file:
#             files.append(os.path.join(r, file))

# sample = None
sample = Sample(path=here + '/' + 'data/lut/AST1.json')
# # seesoft = SeeSoft(data=sample.data, comments=True)
# # seesoft.draw(img_path='assets/seesoft.png')
luacode = None
seesoft = None
# # luacode = LuaCode(data=sample.data)
# # scatterplot = ScatterPlot(data=sample.data)
# # tree = Tree(data=sample.data)
scatterplot = None
tree = None
# # clusters = Clusters(sample=sample)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H3(
            children='CodeNNVis',
            className='ten columns'
        )],
        className="row"
    ),
    html.Div([
        'Module sample to be analyzed: '],
        style={'margin-bottom': '10px'},
        className='row'
    ),
    html.Div([
        dcc.Input(
            id='module-input',
            value='data/...',
            style={'width': '300px'}
        ),
        html.Button(
            'Submit',
            id='module-input-button',
            n_clicks=0,
            style={'margin-left': '10px'},
            className='button-primary'
        )],
        className='row'
    ),
    html.Div(id='hidden-div',
             style={'display': 'none'}),
    html.Div([
        html.H5('Source code')],
        style={'margin-top': '20px'},
        className='row'
    ),
    html.Div(
        # id='first-part',
        children=[
            html.Div(
                id='lua-code',
                children=[],
                style={
                    # 'outline': '2px solid black',
                    'height': '800px',
                    'float': 'left',
                    'width': '660px',
                    'padding-left': '10px',
                    'padding-right': '10px',
                    'background-color': 'red'
                }
            ),
            # html.Div(
            #     id='left-column',
            #     children=[],
            #     style={
            #         'float': 'left',
            #         'width': '660px',
            #         'padding': '10px',
            #         'background-color': 'red'
            #     }
            #     # className='6 columns'
            # ),
            html.Div(
                id='right-column',
                children=[],
                style={
                    'float': 'left',
                    'width': '660px',
                    'padding': '10px',
                    'background-color': 'blue'
                }
                # className='6 columns'
            ),
        ],
        className='row'
    ),

    # html.Div(
    #     id='lua-code',
    #     children=[],
    #     style={
    #         # 'outline': '2px solid black',
    #         'height': '800px',
    #         # 'padding-top': '20px',
    #         # 'padding-left': '30px'
    #     }
    # )
    ],
    className='ten columns offset-by-one'
)


@app.callback(
    Output('lua-code', 'children'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_left_column(n_clicks, value):
    global sample
    global luacode
    global seesoft

    if n_clicks > 0:
        # sample = Sample(path=here + '/' + str(value))
        luacode = LuaCode(path=value)
        # seesoft = SeeSoft(data=sample.data, comments=True)
        # seesoft.draw(img_path='assets/seesoft.png')

        return [
            luacode.view(dash_id='lua-code-content', columns='8'),
            # seesoft.view(dash_id='seesoft-content', columns='4')
        ]

        # return html.Pre(
        #     id='lua-code-content',
        #     children=luacode.get_children('lua-code-content'),
        #     style={
        #         'background-color': COLORS['code-background'],
        #         'font-family': 'Courier, monospace',
        #         'color': 'black',
        #         'font-size': '10px',
        #         'line-height': LUA_LINE_HEIGHT,
        #         'padding': '20px',
        #         'height': '730px',
        #         'overflow': 'auto'
        #     },
        #     className='8 columns'
        # )


@app.callback(
    Output('right-column', 'children'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_right_column(n_clicks, value):
    # global sample
    global scatterplot
    global tree

    if n_clicks > 0:
        scatterplot = ScatterPlot(path=value)
        tree = Tree(path=value)

        return [
            scatterplot.view(dash_id='scatterplot-content', columns='6'),
            tree.view(dash_id='tree-content', columns='6')
        ]


if __name__ == '__main__':
    app.run_server(debug=True)
