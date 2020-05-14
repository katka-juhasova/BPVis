import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from keras.models import load_model
from network.clustering import ClusteringLayer
import components.layout as layout
from sample import Sample
from components.luacode import LuaCode
from components.seesoft import SeeSoft
from components.scatterplot import ScatterPlot
from components.tree import Tree
from components.clusters import Clusters
from components.prediction import Prediction
from components.network import Network
import time

DIMENSIONS = 10

here = os.path.dirname(os.path.realpath(__file__))
model_path = here + '/network/clustering_model_10.h5'
model = load_model(model_path,
                   custom_objects={'ClusteringLayer': ClusteringLayer})
luacode = None
seesoft = None
train1_seesoft = None
scatterplot = None
tree = None
sample = None
click_counter = 0
clusters = Clusters()
prediction = None


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
        'Source code sample to be analyzed: '],
        style={'margin-bottom': '10px'},
        className='row'
    ),
    html.Div([
        dcc.Input(
            id='module-input',
            placeholder='Enter JSON file name',
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
        html.H4('Source code visualization')],
        style={'margin-top': '20px'},
        className='row'
    ),
    html.Div(
        children=[
            html.Div(
                id='input-luacode',
                children=[
                    layout.get_empty_div(height=750)
                ],
                style={
                    'height': '800px',
                    'float': 'left',
                    'width': '520px',
                    'padding-left': '10px',
                    'padding-right': '10px',
                }
            ),
            dcc.Graph(
                id='seesoft-content',
                figure=layout.get_empty_figure(height=750),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '750px',
                    'float': 'left',
                    'width': '200px',
                    'padding': '10px',
                }
            ),
            html.Img(
                src=layout.get_legend_image(),
                style={
                    'position': 'absolute',
                    'top': '1000px',
                    'left': '180px'
                }
            ),
            html.H6(
                'Prediction',
                style={
                    'position': 'absolute',
                    'top': '1050px',
                    'margin-left': '10px'
                }
            ),
            dcc.Graph(
                id='prediction-content',
                figure=layout.get_empty_figure(height=200),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '120px',
                    'width': '520px',
                    'position': 'absolute',
                    'top': '1100px',
                    'margin-left': '10px'
                }
            ),
            html.Button(
                id='network-button',
                children=[
                    'View/hide full network architecture with activations'
                ],
                style={
                    'position': 'absolute',
                    'top': '1220px',
                    'left': '150px',
                    'margin-left': '10px'
                },
                className='link-button'
            ),
            html.Div(
                id='input-diagrams',
                children=[
                    html.H6('AST nodes order'),
                    dcc.Graph(
                        id='scatterplot-content',
                        figure=layout.get_empty_figure(height=200),
                        config={
                            'displayModeBar': False
                        },
                        style={
                            'height': '200px',
                        }
                    ),
                    html.H6('Input AST structure'),
                    dcc.Graph(
                        id='tree-content',
                        figure=layout.get_empty_figure(height=250),
                        config={
                            'displayModeBar': False
                        },
                        style={
                            'height': '250px',
                        }
                    ),
                    html.H6('Cluster diagram'),
                    dcc.RadioItems(
                        id='cluster-radio',
                        options=[
                            {'label': 'PCA', 'value': 'pca'},
                            {'label': 'T-SNE', 'value': 'tsne'}
                        ],
                        value='pca',
                        labelStyle={'display': 'inline-block'}
                    ),
                    dcc.Graph(
                        id='clusters-content',
                        figure=layout.get_empty_figure(height=500),
                        config={
                            'displayModeBar': False
                        },
                        style={
                            'height': '500px',
                        }
                    ),
                ],
                style={
                    'float': 'left',
                    'width': '720px',
                    'padding-left': '10px',
                    'padding-right': '10px',
                    'padding-bottom': '10px',
                }
            ),
        ],
        className='row'
    ),
    html.Div(
        id='network-div',
        children=[
            html.H6('Network architecture with activations'),
            dcc.Graph(
                id='sample-network',
                config={
                    'displayModeBar': False
                },
                figure=layout.get_empty_figure(height=900),
                style={
                    'margin': '0 auto'
                }
            ),
        ],
        style={
            'display': 'none',
            'height': '930px',
            'padding': '10px',
            'margin-right': '10px'
        },
        className='row',
    ),
    html.Div([
        html.H4('Data comparing')],
        style={'margin-top': '20px'},
        className='row'
    ),
    dcc.RadioItems(
        id='compare-radio',
        options=[
            {'label': 'AST', 'value': 'ast'},
            {'label': 'Coloured code', 'value': 'code'}
        ],
        value='ast',
        labelStyle={'display': 'inline-block'}
    ),
    html.Div(
        children=[
            html.Div('Analyzed sample', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'}),
            html.Div('Train sample #1', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'}),
            html.Div('Train sample #2', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'}),
            html.Div('Train sample #3', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'}),
            html.Div('Train sample #4', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'}),
            html.Div('Train sample #5', style={'width': '230px',
                                               'float': 'left',
                                               'margin': '10px'})
        ],
        className='row'
    ),
    html.Div(
        children=[
            html.Pre(
                [],
                style={'width': '230px', 'float': 'left',
                       'margin-right': '20px'}
            ),
            dcc.Input(
                id='train1-input',
                placeholder='Sample #1',
                style={'width': '185px', 'margin-left': '10px'}
            ),
            html.Button(
                '✓',
                id='train1-yes-button',
                n_clicks=0,
                style={'margin-left': '5px', 'margin-rignt': '10px'},
                className='yes-button'
            ),
            dcc.Input(
                id='train2-input',
                placeholder='Sample #2',
                style={'width': '185px', 'margin-left': '23px'}
            ),
            html.Button(
                '✓',
                id='train2-yes-button',
                n_clicks=0,
                style={'margin-left': '5px', 'margin-rignt': '10px'},
                className='yes-button'
            ),
            dcc.Input(
                id='train3-input',
                placeholder='Sample #3',
                style={'width': '185px', 'margin-left': '22px'}
            ),
            html.Button(
                '✓',
                id='train3-yes-button',
                n_clicks=0,
                style={'margin-left': '5px', 'margin-rignt': '10px'},
                className='yes-button'
            ),
            dcc.Input(
                id='train4-input',
                placeholder='Sample #4',
                style={'width': '185px', 'margin-left': '22px'}
            ),
            html.Button(
                '✓',
                id='train4-yes-button',
                n_clicks=0,
                style={'margin-left': '5px', 'margin-rignt': '10px'},
                className='yes-button'
            ),
            dcc.Input(
                id='train5-input',
                placeholder='Sample #5',
                style={'width': '185px', 'margin-left': '22px'}
            ),
            html.Button(
                '✓',
                id='train5-yes-button',
                n_clicks=0,
                style={'margin-left': '5px'},
                className='yes-button'
            )
        ],
        className='row'
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='sample-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
            dcc.Graph(
                id='train1-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
            dcc.Graph(
                id='train2-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
            dcc.Graph(
                id='train3-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
            dcc.Graph(
                id='train4-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
            dcc.Graph(
                id='train5-prediction',
                figure=layout.get_empty_figure(height=100),
                config={
                    'displayModeBar': False
                },
                style={
                    'height': '100px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px'
                }
            ),
        ],
        className='row'
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='sample-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
            dcc.Graph(
                id='train1-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
            dcc.Graph(
                id='train2-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
            dcc.Graph(
                id='train3-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
            dcc.Graph(
                id='train4-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
            dcc.Graph(
                id='train5-content',
                figure=layout.get_empty_figure(height=650),
                config={
                    'displayModeBar': False
                },
                style={
                    'max-height': '650px',
                    'float': 'left',
                    'width': '230px',
                    'padding': '10px',
                }
            ),
        ],
        className='row'
    ),
    html.Pre([], style={'height': '50px'}),
],
    className='ten columns offset-by-one'
)


@app.callback(
    Output('input-luacode', 'children'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_luacode(n_clicks, value):
    global luacode

    if n_clicks > 0:
        luacode = LuaCode(path='data/' + value)
        return luacode.view(dash_id='luacode-content')

    else:
        return layout.get_empty_div(750)


@app.callback(
    Output('seesoft-content', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_seesoft(n_clicks, value):
    global seesoft

    if n_clicks > 0:
        seesoft = SeeSoft(path='data/' + value, comments=True)
        seesoft.draw()
        return seesoft.get_figure()

    else:
        return layout.get_empty_figure(height=750)


@app.callback(
    Output('scatterplot-content', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_scatterplot(n_clicks, value):
    global scatterplot

    if n_clicks > 0:
        scatterplot = ScatterPlot(path='data/' + value)
        return scatterplot.get_figure(show_legend=True, show_text=True)

    else:
        return layout.get_empty_figure(height=200)


@app.callback(
    Output('tree-content', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_tree(n_clicks, value):
    global tree

    if n_clicks > 0:
        tree = Tree(path='data/' + value)
        return tree.get_figure(horizontal=True)

    else:
        return layout.get_empty_figure(height=250)


@app.callback(
    Output('clusters-content', 'figure'),
    [Input('module-input-button', 'n_clicks'),
     Input('cluster-radio', 'value'),
     Input('train1-yes-button', 'n_clicks'),
     Input('train2-yes-button', 'n_clicks'),
     Input('train3-yes-button', 'n_clicks'),
     Input('train4-yes-button', 'n_clicks'),
     Input('train5-yes-button', 'n_clicks')],
    [State('module-input', 'value'),
     State('train1-input', 'value'),
     State('train2-input', 'value'),
     State('train3-input', 'value'),
     State('train4-input', 'value'),
     State('train5-input', 'value')]
)
def update_clusters(n_clicks1, value1, n_clicks2, n_clicks3, n_clicks4,
                    n_clicks5, n_clicks6, value2, value3,  value4,  value5,
                    value6,  value7):
    global click_counter
    global sample
    global clusters

    # n_clicks1 = man submit button
    # n_clicks2 = submit train1
    # value1 = pca/tsne
    # value2 = analyzed module name
    # value3 = train1 name
    # etc.

    if n_clicks1 > 0:
        # handle train1 sample highlight
        if n_clicks2 > 0:
            if value3 == '':
                clusters.train_samples[0] = None
            else:
                clusters.train_samples[0] = value3

        # handle train2 sample highlight
        if n_clicks3 > 0:
            if value4 == '':
                clusters.train_samples[1] = None
            else:
                clusters.train_samples[1] = value4

        # handle train3 sample highlight
        if n_clicks4 > 0:
            if value5 == '':
                clusters.train_samples[2] = None
            else:
                clusters.train_samples[2] = value5

        # handle train4 sample highlight
        if n_clicks5 > 0:
            if value6 == '':
                clusters.train_samples[3] = None
            else:
                clusters.train_samples[3] = value6

        # handle train5 sample highlight
        if n_clicks6 > 0:
            if value7 == '':
                clusters.train_samples[4] = None
            else:
                clusters.train_samples[4] = value7

        if n_clicks1 == click_counter:
            return clusters.get_figure(algorithm=value1)

        click_counter = n_clicks1
        sample = Sample(path='data/' + value2, model=model)
        clusters.add_sample(sample)
        return clusters.get_figure(algorithm=value1)

    else:
        return layout.get_empty_figure(height=500)


@app.callback(
    Output('prediction-content', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_input_prediction(n_clicks, value):
    global prediction
    global sample

    if n_clicks > 0:
        while not sample:
            time.sleep(1.)

        prediction = Prediction(sample=sample)
        return prediction.get_figure()

    else:
        return layout.get_empty_figure(height=120)


@app.callback(
    Output('sample-prediction', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_sample_prediction(n_clicks, value):
    global prediction

    if n_clicks > 0:
        while not prediction:
            time.sleep(1.)

        return prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('sample-content', 'figure'),
    [Input('module-input-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('module-input', 'value')]
)
def update_sample_seesoft(n_clicks, value1, value2):
    global seesoft
    global tree

    if n_clicks > 0:
        if value1 == 'code':
            while not seesoft:
                time.sleep(1.)
            return seesoft.get_figure(small=True)

        else:
            while not tree:
                time.sleep(1.)
            return tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('train1-prediction', 'figure'),
    [Input('train1-yes-button', 'n_clicks')],
    [State('train1-input', 'value')]
)
def update_train1_prediction(n_clicks, value):
    global model
    if value == '':
        return layout.get_empty_figure(height=100)

    if n_clicks > 0:
        local_sample = Sample(path='data/' + value, model=model)
        local_prediction = Prediction(sample=local_sample)
        return local_prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('train1-content', 'figure'),
    [Input('train1-yes-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('train1-input', 'value')]
)
def update_train1_content(n_clicks, value1, value2):
    if value2 == '':
        return layout.get_empty_figure(height=650)

    if n_clicks > 0:
        if value1 == 'code':
            local_seesoft = SeeSoft(path='data/' + value2, comments=True)
            local_seesoft.draw()
            return local_seesoft.get_figure(small=True)

        else:
            local_tree = Tree(path='data/' + value2)
            return local_tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('train2-prediction', 'figure'),
    [Input('train2-yes-button', 'n_clicks')],
    [State('train2-input', 'value')]
)
def update_train2_prediction(n_clicks, value):
    global model
    if value == '':
        return layout.get_empty_figure(height=100)

    if n_clicks > 0:
        local_sample = Sample(path='data/' + value, model=model)
        local_prediction = Prediction(sample=local_sample)
        return local_prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('train2-content', 'figure'),
    [Input('train2-yes-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('train2-input', 'value')]
)
def update_train2_content(n_clicks, value1, value2):
    if value2 == '':
        return layout.get_empty_figure(height=650)

    if n_clicks > 0:
        if value1 == 'code':
            local_seesoft = SeeSoft(path='data/' + value2, comments=True)
            local_seesoft.draw()
            return local_seesoft.get_figure(small=True)

        else:
            local_tree = Tree(path='data/' + value2)
            return local_tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('train3-prediction', 'figure'),
    [Input('train3-yes-button', 'n_clicks')],
    [State('train3-input', 'value')]
)
def update_train1_prediction(n_clicks, value):
    global model
    if value == '':
        return layout.get_empty_figure(height=100)

    if n_clicks > 0:
        local_sample = Sample(path='data/' + value, model=model)
        local_prediction = Prediction(sample=local_sample)
        return local_prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('train3-content', 'figure'),
    [Input('train3-yes-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('train3-input', 'value')]
)
def update_train1_content(n_clicks, value1, value2):
    if value2 == '':
        return layout.get_empty_figure(height=650)

    if n_clicks > 0:
        if value1 == 'code':
            local_seesoft = SeeSoft(path='data/' + value2, comments=True)
            local_seesoft.draw()
            return local_seesoft.get_figure(small=True)

        else:
            local_tree = Tree(path='data/' + value2)
            return local_tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('train4-prediction', 'figure'),
    [Input('train4-yes-button', 'n_clicks')],
    [State('train4-input', 'value')]
)
def update_train1_prediction(n_clicks, value):
    global model
    if value == '':
        return layout.get_empty_figure(height=100)

    if n_clicks > 0:
        local_sample = Sample(path='data/' + value, model=model)
        local_prediction = Prediction(sample=local_sample)
        return local_prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('train4-content', 'figure'),
    [Input('train4-yes-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('train4-input', 'value')]
)
def update_train1_content(n_clicks, value1, value2):
    if value2 == '':
        return layout.get_empty_figure(height=650)

    if n_clicks > 0:
        if value1 == 'code':
            local_seesoft = SeeSoft(path='data/' + value2, comments=True)
            local_seesoft.draw()
            return local_seesoft.get_figure(small=True)

        else:
            local_tree = Tree(path='data/' + value2)
            return local_tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('train5-prediction', 'figure'),
    [Input('train5-yes-button', 'n_clicks')],
    [State('train5-input', 'value')]
)
def update_train1_prediction(n_clicks, value):
    global model
    if value == '':
        return layout.get_empty_figure(height=100)

    if n_clicks > 0:
        local_sample = Sample(path='data/' + value, model=model)
        local_prediction = Prediction(sample=local_sample)
        return local_prediction.get_figure(small=True)

    else:
        return layout.get_empty_figure(height=100)


@app.callback(
    Output('train5-content', 'figure'),
    [Input('train5-yes-button', 'n_clicks'),
     Input('compare-radio', 'value')],
    [State('train5-input', 'value')]
)
def update_train1_content(n_clicks, value1, value2):
    if value2 == '':
        return layout.get_empty_figure(height=650)

    if n_clicks > 0:
        if value1 == 'code':
            local_seesoft = SeeSoft(path='data/' + value2, comments=True)
            local_seesoft.draw()
            return local_seesoft.get_figure(small=True)

        else:
            local_tree = Tree(path='data/' + value2)
            return local_tree.get_figure()

    else:
        return layout.get_empty_figure(height=650)


@app.callback(
    Output('sample-network', 'figure'),
    [Input('module-input-button', 'n_clicks')],
    [State('module-input', 'value')]
)
def update_network(n_clicks, value):
    global sample

    if n_clicks > 0:
        while not sample:
            time.sleep(1.)

        local_network = Network(sample=sample)
        return local_network.get_figure()

    else:
        return layout.get_empty_figure(height=900)


@app.callback(
    Output('network-div', 'style'),
    [Input('network-button', 'n_clicks')]
)
def show_network(n_clicks):
    if not n_clicks or n_clicks % 2 == 0:
        return {
            'display': 'none',
            'height': '930px',
            'padding': '10px',
            'margin-right': '10px'
        }
    else:
        return {
            'display': 'block',
            'height': '930px',
            'padding': '10px',
            'margin-right': '10px'
        }


app.clientside_callback(
    '''
    function scroll_lua_code_left(clickData) {
        if (clickData) {
            var element = document.getElementById("luacode-content");
            var element_text_id = "luacode-content" + clickData.points[0].text;
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
            if (color == "rgb(248, 172, 97)") {
                element_text.classList.remove("require_animate");
                void element_text.offsetWidth;
                element_text.classList.add("require_animate");
            }
            else if (color == "rgb(169, 208, 165)") {
                element_text.classList.remove("variable_animate");
                void element_text.offsetWidth;
                element_text.classList.add("variable_animate");
            }
            else if (color == "rgb(178, 198, 220)") {
                element_text.classList.remove("function_animate");
                void element_text.offsetWidth;
                element_text.classList.add("function_animate");
            }
            else if (color == "rgb(201, 161, 189)") {
                element_text.classList.remove("interface_animate");
                void element_text.offsetWidth;
                element_text.classList.add("interface_animate");
            }
            else if (color == "rgb(244, 223, 137)") {
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
