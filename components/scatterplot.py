import logging
import json
import urllib
import chardet
from constant import DIAGRAM_COLORS as COLORS
import plotly.graph_objects as go
import dash_core_components as dcc


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class ScatterPlot:
    """
    Class for visualization of the nodes from AST structure of the source code
    without actually capturing the tree structure. The nodes are organized
    linearly creating a scatterplot.

    Attributes
    ----------
    data : dict
        pre-processed data read from the JSON file
    source_code : str
        read original source code, structure of which is represented in
        the attribute data
    traces : dict of dict
        all the nodes and their properties (x, y, text and color) organised
        into dict so that each type of statement is represented by its
        separate trace
    """

    def __init__(self, path=None, url=None, data=None):
        """
        According to the parameters given, the preprocessed data are read
        from .json file (parameter path) or from the given url or
        simply copied from the given parameter data. If none of
        the parameters is provided, the function raises an error. Furthermore,
        the original source code is read and the attribute traces is
        initialized.

        Parameters
        ----------
        path :  str or None, optional
            path to the JSON file, which contains preprocessed .lua source code
            (default is None)
        url : str or None, optional
            url of the JSON file, which contains preprocessed .lua source code
            (default is None)
        data : dict or None, optional
            preprocessed data already read from .json file
        """

        if data:
            self.data = data

        else:
            if all(arg is None for arg in {path, url}):
                raise ValueError('Expected either path or url argument')

            if path:
                with open(path) as f:
                    self.data = json.load(f)

            else:
                log.debug('Loading data file from {}'.format(url))
                with urllib.request.urlopen(url) as url_data:
                    self.data = json.loads(url_data.read().decode())

        self.source_code = self.__read_source_code()
        self.traces = {
            'require': {
                'x': list(),
                'y': list(),
                'text': list(),
                'color': COLORS['require']
            },
            'variable': {
                'x': list(),
                'y': list(),
                'text': list(),
                'color': COLORS['variable']
            },
            'function': {
                'x': list(),
                'y': list(),
                'text': list(),
                'color': COLORS['function']
            },
            'interface': {
                'x': list(),
                'y': list(),
                'text': list(),
                'color': COLORS['interface']
            },
            'other': {
                'x': list(),
                'y': list(),
                'text': list(),
                'color': COLORS['other']
            }
        }

    def __read_source_code(self) -> str:
        """
        Reads and returns lua source code from path or url from the data.

        Returns
        --------
        str
            original lua source code which was preprocessed and stored in
            .json file
        """

        # if there's path provided read form it, otherwise read from url
        if self.data['path']:
            raw_data = open(self.data['path'], 'rb').read()

        else:
            log.debug('Loading module file from {}'.format(self.data['url']))
            url_file = urllib.request.urlopen(self.data['url'])
            raw_data = url_file.read()

        chardet_result = chardet.detect(raw_data)
        if chardet_result['encoding'] not in ['ascii', 'utf-8']:
            raw_data = raw_data.decode('iso-8859-1').encode('utf-8')

        return raw_data.decode('utf-8')

    def __add_node_to_trace(self, node: dict):
        """
        Builds attribute traces so that the scatterplot can be created later.

        Parameters
        ----------
        node : dict
            node read from the JSON file containing all the properties such as
            container tpe, children etc.
        """

        self.traces[node['container']]['x'].append(node['master_index'])
        self.traces[node['container']]['y'].append(node['container'])
        self.traces[node['container']]['text'].append(
            (
                self.source_code[node['position'] - 1:
                                 node['position'] + node['characters_count']]
            ).replace('\n', '<br>')
        )

        # hover text may be too long so it needs to be limited to max 10 lines
        if self.traces[node['container']]['text'][-1].count('<br>') > 10:
            text = self.traces[node['container']]['text'][-1]
            text = text.split('<br>', 9)
            text[-1] = '...'
            text = '<br>'.join(text)
            self.traces[node['container']]['text'][-1] = text

        if 'children' in node:
            for child in node['children']:
                self.__add_node_to_trace(child)

    def __add_traces(self, fig, show_text: bool):
        """
        Adds traces from the attribute traces to the figure.

        Parameters
        ----------
        fig : go.Figure
            go.Figure instance where the scatterplot should be drawn
        show_text : bool
            determines whether the hover info should contain the text (section
            of the source code) represented by each node
        """

        for node in self.data['nodes']:
            self.__add_node_to_trace(node)

        for trace in self.traces:
            fig.add_trace(
                go.Scatter(
                    name=trace,
                    x=self.traces[trace]['x'],
                    y=self.traces[trace]['y'],
                    hovertext=self.traces[trace]['text'] if show_text else '',
                    mode='markers',
                    opacity=0.8,
                    hoverinfo='x+y+text' if show_text else 'x+y',
                    marker={
                        'color': self.traces[trace]['color'],
                        'size': 10,
                        'line': {
                            'width': 0.5,
                            'color': 'white'
                        }
                    }
                )
            )

    def get_figure(self, show_legend=False, show_text=False) -> go.Figure:
        """
        Creates a figure containing scatterplot. The scatterplot consists of
        the nodes from AST structure of the source code without actually
        capturing the tree structure.

        Parameters
        ----------
        show_legend : bool, optional
            determines whether the legend should by displayed
            (default is False)
        show_text : bool, optional
            determines whether the hover info should contain the text (section
            of the source code) represented by each node  (default is False)

        Returns
        -------
        go.Figure
            go.Figure instance containing the scatterplot
        """

        fig = go.Figure()
        self.__add_traces(fig, show_text)

        fig.update_layout(
            template='plotly_white',
            xaxis={
                'rangemode': 'tozero'
            },
            yaxis={'title': 'Container'},
            margin={'l': 40, 'r': 20, 'b': 40, 't': 0},
            showlegend=show_legend,
            legend_orientation="h"
        )

        return fig

    def view(self, dash_id: str, height=None, show_legend=False,
             show_text=False):
        """
        Creates dcc.Graph object which contains the scatterplot.
        The scatterplot consists of the nodes from AST structure of the source
        code without actually capturing the tree structure. It's optional to
        set the height of diagram in pixels.

        Parameters
        ----------
        dash_id : str
            id of the dcc.Graph component
        height : int or None
            height of the diagram (default is None)
        show_legend : bool, optional
            determines whether the legend should by displayed
            (default is False)
        show_text : bool, optional
            determines whether the hover info should contain the text (section
            of the source code) represented by each node  (default is False)

        Returns
        -------
        dcc.Graph
            dcc.Graph instance of the scatterplot
        """

        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(show_legend, show_text),
            style={
                'height': height or '220px'
            }
        )
