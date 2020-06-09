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
    def __init__(self, path=None, url=None, data=None):
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

    def view(self, dash_id: str, height=None,
             show_legend=False, show_text=False):
        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(show_legend, show_text),
            style={
                'height': height or '220px'
            }
        )
