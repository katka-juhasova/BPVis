import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from components.luacode import LuaCode
from components.seesoft import SeeSoft
from components.scatterplot import ScatterPlot
from components.tree import Tree
from components.clusters import Clusters
from components.prediction import Prediction
from components.network import Network
from dash.dependencies import Input, Output
from sample import Sample

DIMENSIONS = 7

path = os.path.dirname(os.path.realpath(__file__)) + '/test_data'
files = list()

# r=root, d=directories, f=files
# list all json files
for r, d, f in os.walk(path):
    for file in f:
        if '.json' in file:
            files.append(os.path.join(r, file))

sample = Sample(files[71])
# file_left = files[71]
file_right = files[71]

seesoft_left = SeeSoft(data=sample.data, comments=True)
seesoft_left.draw(img_path='assets/image_left.png')

seesoft_right = SeeSoft(file_right, comments=True)
seesoft_right.draw(img_path='assets/image_right.png')

luacode_left = LuaCode(data=sample.data)
luacode_right = LuaCode(file_right)

scatterplot_left = ScatterPlot(data=sample.data)
scatterplot_right = ScatterPlot(file_right)

tree_left = Tree(data=sample.data)
tree_right = Tree(file_right)

# clusters = Clusters(sample=sample)
prediction = Prediction(sample=sample)
network = Network(sample=sample)

# external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']

app = dash.Dash(__name__)

app.layout = html.Div([

    # prediction.view(dash_id='prediction', columns='6'),
    network.view(dash_id='network', columns='12')

    # html.Div([
    #     html.H3(children='Source code visualization',
    #             className='ten columns'),
    # ],
    #     className="row"
    # ),
    # html.Div([
    #     'Module sample to be analyzed: '],
    #     style={'margin-bottom': '10px'},
    #     className='row'
    # ),
    # html.Div([
    #     dcc.Input(
    #         id='input-module',
    #         value='test_data/...',
    #         style={'width': '300px'}
    #     ),
    #     html.Button(
    #         'Submit',
    #         id='input-module-button',
    #         n_clicks=0,
    #         style={'margin-left': '10px'},
    #         className='button-primary'
    #     )],
    #     className='row'
    # ),
    # html.Div(id='hidden-div-left',
    #          style={'display': 'none'}),
    # html.Div(id='hidden-div-right',
    #          style={'display': 'none'}),
    # html.Div(
    #     children=[
    #         luacode_left.view(dash_id='lua-code-left', columns='4'),
    #         seesoft_left.view(dash_id='see-soft-left', columns='2',
    #                           width='240px', height='750px'),
    #         luacode_right.view(dash_id='lua-code-right', columns='4'),
    #         seesoft_right.view(dash_id='see-soft-right', columns='2',
    #                            width='240px', height='750px')
    #     ],
    #     # style={'padding': '3vh'},
    #     className='row'
    # ),
    # html.Div(
    #     children=[
    #         scatterplot_left.view(
    #             dash_id='scatter-plot-left',
    #             columns='6',
    #             show_text=True,
    #             show_legend=True),
    #         scatterplot_right.view(
    #             dash_id='scatter-plot-right',
    #             columns='6',
    #             show_legend=True,
    #             show_text=True)
    #     ],
    #     style={'padding': '3vh'},
    #     className='row'
    # ),
    # html.Div(
    #     children=[
    #         tree_left.view(dash_id='tree-left', columns='6'),
    #         tree_right.view(dash_id='tree-right', columns='6')
    #     ],
    #     className='row'
    # ),
    # html.Div(
    #     children=[
    #         # clusters.view(dash_id='clusters-left', columns='6',
    #         #               algorithm='PCA'),
    #         # clusters.view(dash_id='clusters-right', columns='6',
    #         #               algorithm='TSNE')
    #     ],
    #     className='row'
    # )
    ]
)
#
# # only works properly when seesoft is drawn with comments
# # seesoft and luacode interaction for left part of the screen
# app.clientside_callback(
#     '''
#     function scroll_lua_code_left(clickData) {
#         if (clickData) {
#             var element = document.getElementById("lua-code-left");
#             var element_text_id = "lua-code-left" + clickData.points[0].text;
#             var element_text = document.getElementById(element_text_id);
#             var color = element_text.style.backgroundColor;
#             var bounding = element.getBoundingClientRect();
#             var text_bounding = element_text.getBoundingClientRect();
#
#             // handle possible vertical scrolling
#             if (text_bounding.top < bounding.top ||
#                 text_bounding.bottom > bounding.bottom) {
#                 element.scrollTop = clickData.points[0].customdata;
#             }
#
#             // handle highlighting
#             if (color == "rgb(255, 173, 122)") {
#                 element_text.classList.remove("require_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("require_animate");
#             }
#             else if (color == "rgb(117, 235, 135)") {
#                 element_text.classList.remove("variable_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("variable_animate");
#             }
#             else if (color == "rgb(158, 203, 255)") {
#                 element_text.classList.remove("function_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("function_animate");
#             }
#             else if (color == "rgb(229, 141, 240)") {
#                 element_text.classList.remove("interface_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("interface_animate");
#             }
#             else if (color == "rgb(255, 236, 145)") {
#                 element_text.classList.remove("other_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("other_animate");
#             }
#             else {
#                 element_text.classList.remove("comment_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("comment_animate");
#             }
#         }
#         return "";
#     }
#     ''',
#     Output('hidden-div-left', 'children'),
#     [Input('see-soft-left', 'clickData')]
# )
#
# # seesoft and luacode interaction for the right part of the screen
# app.clientside_callback(
#     '''
#     function scroll_lua_code_right(clickData) {
#         if (clickData) {
#             var element = document.getElementById("lua-code-right");
#             var element_text_id = "lua-code-right" + clickData.points[0].text;
#             var element_text = document.getElementById(element_text_id);
#             var color = element_text.style.backgroundColor;
#             var bounding = element.getBoundingClientRect();
#             var text_bounding = element_text.getBoundingClientRect();
#
#             // handle possible vertical scrolling
#             if (text_bounding.top < bounding.top ||
#                 text_bounding.bottom > bounding.bottom) {
#                 element.scrollTop = clickData.points[0].customdata;
#             }
#
#             // handle highlighting
#             if (color == "rgb(255, 173, 122)") {
#                 element_text.classList.remove("require_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("require_animate");
#             }
#             else if (color == "rgb(117, 235, 135)") {
#                 element_text.classList.remove("variable_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("variable_animate");
#             }
#             else if (color == "rgb(158, 203, 255)") {
#                 element_text.classList.remove("function_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("function_animate");
#             }
#             else if (color == "rgb(229, 141, 240)") {
#                 element_text.classList.remove("interface_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("interface_animate");
#             }
#             else if (color == "rgb(255, 236, 145)") {
#                 element_text.classList.remove("other_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("other_animate");
#             }
#             else {
#                 element_text.classList.remove("comment_animate");
#                 void element_text.offsetWidth;
#                 element_text.classList.add("comment_animate");
#             }
#         }
#         return "";
#     }
#     ''',
#     Output('hidden-div-right', 'children'),
#     [Input('see-soft-right', 'clickData')]
# )
#
# # maybe lua code sections and seesoft interaction could be fixed so that
# # whole node text would be one section instead of one line or part of the line


if __name__ == '__main__':
    app.run_server(debug=True)
