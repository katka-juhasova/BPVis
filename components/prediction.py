import logging
from sample import Sample
import plotly.graph_objects as go
from constant import WHITE_TO_BLUE
import dash_core_components as dcc

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Prediction:
    """
    Class for visualization of the prediction of the neural network.
    The prediction is visualized using a categorical heatmap.

    Attributes
    ----------
    label : int
        label of the cluster, to which the sample was assigned
        (prediction of the neural network)
    output_layer : list
        activations from the last layer of the neural network
    """

    def __init__(self, sample: Sample):
        """
        Gets the label and the activations from the last layer and stores
        the values in the attributes.

        Parameters
        ----------
        sample : Sample
            contains everything needed for visualization of sample including
            the information about activations on the last layer and the label
        """

        self.label = sample.label

        # read output layer from sample
        last_layer = list(sample.activations.keys())[-1]
        self.output_layer = sample.activations[last_layer][0].tolist()

    def get_figure(self, height=None, small=False):
        """
        Creates the figure containing the categorical heatmap representing
        the prediction of the neural network.

        Parameters
        ----------
        height : int or None, optional
            height of the diagram in pixels (default is None)
        small : bool, optional
            determines the size of the diagram, if True, the size is
            significantly smaller than the default size (default is False)

        Returns
        -------
        go.Figure
            go.Figure instance of categorical heatmap representing
            the prediction of the neural network
        """

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

        if small:
            fig.update_layout(
                height=100,
                xaxis={'tickangle': 45},
                yaxis={'visible': False},
                margin={'l': 0, 'r': 20, 't': 0}
            )

        else:
            fig.update_layout(
                height=height or 120,
                xaxis={'tickangle': 45},
                yaxis={'visible': False},
                margin={'l': 10, 'r': 20, 't': 0}
            )

        return fig

    def view(self, dash_id: str):
        """
        Creates dcc.Graph object which contains the categorical heatmap
        representing the prediction of the neural network.

        Parameters
        ----------
        dash_id : str
            id of the dcc.Graph component

        Returns
        -------
        dcc.Graph
            dcc.Graph instance of the categorical heatmap representing
            the prediction of the neural network
        """

        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure()
        )
