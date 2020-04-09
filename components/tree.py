import logging
import json
import urllib
from igraph import Graph
import plotly.graph_objects as go
from constant import COLORS
from constant import COLUMNS
import dash_core_components as dcc


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Tree:
    def __init__(self, path=None, url=None):
        if all(arg is None for arg in {path, url}):
            raise ValueError('Expected either path or url argument')

        if path:
            with open(path) as f:
                self.data = json.load(f)
        else:
            log.debug('Loading data file from {}'.format(url))
            with urllib.request.urlopen(url) as url_data:
                self.data = json.loads(url_data.read().decode())

        # all edges between nodes
        self.edges = list()
        # color for each node
        self.colors = ([COLORS['plot-line']]
                       + ['' for x in range(self.data['nodes_count'])])
        # text for each node
        self.text = ['root'] + ['' for x in range(self.data['nodes_count'])]

    def __add_child_edges(self, node: dict):
        for child in node['children']:
            self.edges.append((node['master_index'], child['master_index']))
            self.colors[child['master_index']] = COLORS[child['container']]
            self.text[child['master_index']] = '({}, {})'.format(
                child['master_index'], child['container'])

            if 'children' in child:
                self.__add_child_edges(child)

    def get_figure(self):
        # nodes from .json plus root node
        nodes_count = self.data['nodes_count'] + 1

        # edges from root to the nodes of depth 1
        for node in self.data['nodes']:
            self.edges.append((0, node['master_index']))
            self.colors[node['master_index']] = COLORS[node['container']]
            self.text[node['master_index']] = '({}, {})'.format(
                node['master_index'], node['container'])

            # all other edges to child nodes
            if 'children' in node:
                self.__add_child_edges(node)

        graph = Graph(n=self.data['nodes_count'] + 1, directed=True)
        graph.add_edges(self.edges)

        # build layout with Reingold-Tilford algorithm
        layout = graph.layout_reingold_tilford(mode='out', root=[0])
        # node positions in graph
        positions = {k: layout[k] for k in range(nodes_count)}
        max_y = max([layout[k][1] for k in range(nodes_count)])

        # count node and edge positions and switch original x and y
        # coordinates so that tree would branch horizontally
        nodes_x = [2 * max_y - positions[k][1] for k in range(len(positions))]
        nodes_y = [positions[k][0] for k in range(len(positions))]
        edges_x = list()
        edges_y = list()

        for edge in self.edges:
            edges_y += [positions[edge[0]][0], positions[edge[1]][0], None]
            edges_x += [2 * max_y - positions[edge[0]][1],
                        2 * max_y - positions[edge[1]][1], None]

        # mirror the graph in both directions so that the edges are oriented
        # form left to right and nodes in order from the smallest to
        # the largest
        nodes_x = [-x for x in nodes_x]
        nodes_y = [-y for y in nodes_y]
        edges_x = list(map(lambda x: -x if x else x, edges_x))
        edges_y = list(map(lambda y: -y if y else y, edges_y))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=edges_x,
                y=edges_y,
                mode='lines',
                line={
                    'width': 1,
                    'color': COLORS['plot-line']
                },
                hoverinfo='none'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=nodes_x,
                y=nodes_y,
                mode='markers',
                marker={
                    'size': 10,
                    'color': self.colors,
                    'line': {
                        'width': 0.5,
                        'color': 'white'
                    }
                },
                text=self.text,
                hoverinfo='text',
                opacity=0.8
            )
        )

        # hide axis line, grid, tick labels and title
        axis = dict(showline=False,
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )

        fig.update_layout(
            template='plotly_white',
            title='Input tree',
            xaxis=axis,
            yaxis=axis,
            showlegend=False,
            margin={'l': 40, 'r': 40, 'b': 10, 't': 40}
        )

        return fig

    def view(self, dash_id: str, columns: str, height=None):
        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(),
            style={
                'height': height or '60vh'
            },
            className=COLUMNS[columns]
        )
