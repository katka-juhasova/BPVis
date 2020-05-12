import logging
from sample import Sample
import plotly.graph_objects as go
from constant import WHITE_TO_BLUE
from constant import COLUMNS
import dash_core_components as dcc

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Prediction:
    def __init__(self, sample: Sample):
        self.label = sample.label

        # read output layer from sample
        last_layer = list(sample.activations.keys())[-1]
        self.output_layer = sample.activations[last_layer][0].tolist()

    def get_figure(self, height=None):
        x = ['Label {}'.format(i) for i in range(len(self.output_layer))]
        x[self.label] = '<b>' + x[self.label] + '<b>'
        y = [0 for _ in range(len(self.output_layer))]

        fig = go.Figure(
            data=go.Heatmap(
                z=self.output_layer,
                x=x,
                y=y,
                zmin=0,
                zmax=1,
                showscale=False,
                hoverinfo='z',
                colorscale=WHITE_TO_BLUE,
            )
        )

        fig.update_layout(
            # width=400,
            height=height or 120,
            xaxis={'tickangle': 45},
            yaxis={'visible': False},
            margin={'l': 10, 'r': 20, 't': 0}
        )

        return fig

    def view(self, dash_id: str, columns=None):
        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(),
            # className=COLUMNS[columns]
        )
