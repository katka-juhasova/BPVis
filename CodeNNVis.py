import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import components.layout as layout
from sample import Sample
from components.luacode import LuaCode
from components.seesoft import SeeSoft
from components.scatterplot import ScatterPlot
from components.tree import Tree
from components.clusters import Clusters
# from constant import COLORS
# from constant import LUA_LINE_HEIGHT


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
        children=[
            html.Div(
                id='input-luacode',
                children=[],
                style={
                    # 'outline': '2px solid black',
                    'height': '800px',
                    'float': 'left',
                    'width': '520px',
                    'padding-left': '10px',
                    'padding-right': '10px',
                    'background-color': 'red'
                }
            ),
            # html.Div(
            #     id='input-seesoft',
            #     children=[],
            #     style={
            #         # 'outline': '2px solid black',
            #         'height': '800px',
            #         'float': 'left',
            #         'width': '200px',
            #         'padding-left': '10px',
            #         'padding-right': '10px',
            #         'background-color': 'red'
            #     }
            # ),
            dcc.Graph(
                id='seesoft-content',
                figure=layout.get_empty_figure(),
                config={
                    'displayModeBar': False
                },
                style={
                    # 'outline': '2px solid black',
                    'height': '800px',
                    'float': 'left',
                    'width': '200px',
                    'padding': '10px',
                    'background-color': 'yellow'
                }
            ),
            html.Div(
                id='input-diagrams',
                children=[],
                style={
                    'float': 'left',
                    'width': '720px',
                    'padding': '10px',
                    'background-color': 'blue'
                }
            ),
        ],
        className='row'
    ),
    ],
    className='ten columns offset-by-one'
)


@app.callback(
    Output('input-luacode', 'children'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_luacode(n_clicks, value):
    global sample
    global luacode

    if n_clicks > 0:
        # sample = Sample(path=here + '/' + str(value))
        luacode = LuaCode(path=value)

        return luacode.view(dash_id='lua-code-content')


@app.callback(
    Output('seesoft-content', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_seesoft(n_clicks, value):
    global seesoft

    if n_clicks > 0:
        seesoft = SeeSoft(path=value, comments=True)
        seesoft.draw(img_path='assets/seesoft.png')
        # return layout.get_colorful_figure()
        return seesoft.get_figure()
        # return seesoft.view(dash_id='seesoft-content')

    else:
        return layout.get_empty_figure()


@app.callback(
    Output('input-diagrams', 'children'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_diagrams(n_clicks, value):
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


app.clientside_callback(
    '''
    function scroll_lua_code_left(clickData) {
        if (clickData) {
            var element = document.getElementById("lua-code-content");
            var element_text_id = "lua-code-content" + clickData.points[0].text;
            var element_text = document.getElementById(element_text_id);
            var color = element_text.style.backgroundColor;
            var bounding = element.getBoundingClientRect();
            var text_bounding = element_text.getBoundingClientRect();

            // handle possible vertical scrolling
            if (text_bounding.top < bounding.top ||
                text_bounding.bottom > bounding.bottom) {
                element.scrollTop = clickData.points[0].customdata;
            }

            // handle highlighting
            if (color == "rgb(255, 173, 122)") {
                element_text.classList.remove("require_animate");
                void element_text.offsetWidth;
                element_text.classList.add("require_animate");
            }
            else if (color == "rgb(117, 235, 135)") {
                element_text.classList.remove("variable_animate");
                void element_text.offsetWidth;
                element_text.classList.add("variable_animate");
            }
            else if (color == "rgb(158, 203, 255)") {
                element_text.classList.remove("function_animate");
                void element_text.offsetWidth;
                element_text.classList.add("function_animate");
            }
            else if (color == "rgb(229, 141, 240)") {
                element_text.classList.remove("interface_animate");
                void element_text.offsetWidth;
                element_text.classList.add("interface_animate");
            }
            else if (color == "rgb(255, 236, 145)") {
                element_text.classList.remove("other_animate");
                void element_text.offsetWidth;
                element_text.classList.add("other_animate");
            }
            else {
                element_text.classList.remove("comment_animate");
                void element_text.offsetWidth;
                element_text.classList.add("comment_animate");
            }
        }
        return "";
    }
    ''',
    Output('hidden-div', 'children'),
    [Input('seesoft-content', 'clickData')]
)

if __name__ == '__main__':
    app.run_server(debug=True)
