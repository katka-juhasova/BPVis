import os
import logging
from sample import Sample
import pandas as pd
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from constant import CLUSTER_COLORS
from constant import COLUMNS
import dash_core_components as dcc

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

TRAIN_SAMPLES_NUM = 5
CSV_PATH = (os.path.dirname(os.path.realpath(__file__))
            + '/../network/train_data_activations_layer4.csv')


class Clusters:
    """
    Class for cluster visualization of all train data together with currently
    analyzed sample and possibly 5 more highlighted train samples.

    Attributes
    ----------
    train_samples : list of str
        list of max 5 JSON samples, e.g. '30log/AST1.json'
    train_data : pd.dataFrame
        train data predictions (last layer activations + label) loaded from
        network/train_data_activations_layer4.csv
    sample_data : pd.dataFrame
        activations from the last layer and prediction for currently analyzed
        sample
    tsne_traces : list of dict
        list of dict for every possible label (result of prediction), each
        dict contains t-SNE coordinates of train data samples which were
        labeled with the corresponding label
    tsne_sample_trace : dict
        x and y coordinates of currently analyzed sample in diagram using t-SNE
        algorithm for reduction of dimensionality
    pca_traces : list of dict
        list of dict for every possible label (result of prediction), each
        dict contains PCA coordinates of train data samples which were
        labeled with the corresponding label
    pca_sample_trace : dict
        x and y coordinates of currently analyzed sample in diagram using PCA
        for reduction of dimensionality
    """

    def __init__(self, sample=None):
        """
        Reads train data activations and predictions from
        network/train_data_activations_layer4.csv. If the sample is provided,
        prediction data and activations are assigned to sample_data as well as
        coordinates are determined for training data and currently analyzed
        sample using both t-SNE and PCA for dimensionality reduction.

        Parameters
        ----------
        sample : Sample or None, optional
            instance of Sample representing currently analysed sample contained
            in JSON file (default is None)
        """

        self.train_samples = [None for _ in range(TRAIN_SAMPLES_NUM)]
        self.train_data = self.__load_train_data()

        if sample:
            self.sample_data = self.__load_sample_data(sample)
            log.debug('Performing fit_transform for T-SNE...')
            self.tsne_traces, self.tsne_sample_trace = (
                self.__prepare_tsne_traces()
            )
            log.debug('Performing fit_transform for PCA...')
            self.pca_traces, self.pca_sample_trace = (
                self.__prepare_pca_traces()
            )
            log.debug('Successfully finished fit_transform...')

        else:
            self.sample_data = None
            self.tsne_traces = None
            self.tsne_sample_trace = None
            self.pca_traces = None
            self.pca_sample_trace = None

    @staticmethod
    def __load_sample_data(sample: Sample) -> pd.DataFrame:
        """
        Uses data from provided sample to get activations from last layer
        and the prediction (label).

        Parameters
        ----------
        sample : Sample
            instance of Sample representing currently analysed sample contained
            in JSON file

        Returns
        -------
        pd.dataFrame
            a dataFrame containing activations from last layer and prediction
            (label) for the provided sample
        """

        df = pd.DataFrame()
        df['label'] = sample.label
        last_layer = list(sample.activations.keys())[-1]
        activations = sample.activations[last_layer][0].tolist()
        for i, activation in enumerate(activations):
            df['d{}'.format(i)] = [activation]

        return df

    @staticmethod
    def __load_train_data() -> pd.DataFrame:
        """
        Reads and pre-processes train data activations and predictions from
        network/train_data_activations_layer4.csv

        Returns
        -------
        pd.dataFrame
            a dataFrame containing activations from last layer and prediction
            (label) for the train data
        """

        df = pd.read_csv(CSV_PATH)
        df = df.dropna()
        layer = [l for l in df.columns if 'layer' in l][0]
        dimensions = str(df[layer][0]).split(' ')
        dimensions = ['d{}'.format(d) for d in range(len(dimensions))]
        df[dimensions] = df[layer].str.split(expand=True)
        df = df.drop(columns=[layer])

        return df

    def __prepare_pca_traces(self):
        """
        Performs dimensionality reduction of train data + analyzed sample using
        PCA (Principal Component Analysis).

        Returns
        -------
        list of dict
            list of dict for every possible label (result of prediction), each
            dict contains PCA coordinates of train data samples which were
            labeled with the corresponding label
        dict
            x and y coordinates of currently analyzed sample in diagram using
            PCA for reduction of dimensionality
        """

        labels = self.train_data['label'].tolist()
        data_files = self.train_data['data path'].tolist()
        data = self.train_data.drop(
            columns=['label', 'module path', 'data path'])

        # append sample module and get values
        sample_data = self.sample_data.drop(columns=['label'])
        data = data.append(sample_data, ignore_index=True)
        X = data.values

        X_std = StandardScaler().fit_transform(X)
        pca = PCA()
        pca.fit(X_std)
        pca_results = pca.transform(X_std)

        x = pca_results[:, 0]
        y = pca_results[:, 1]

        dimensions = len(data.columns)
        traces = [
            dict(x=list(), y=list(), text=list()) for _ in range(dimensions)
        ]

        # select sample point from results
        sample_trace = dict(x=x[len(x) - 1], y=y[len(y) - 1])

        # labels list doesn't contain sample data label, so it's OK to do this
        for i, label in enumerate(labels):
            traces[label]['x'].append(x[i])
            traces[label]['y'].append(y[i])
            traces[label]['text'].append(data_files[i])

        return traces, sample_trace

    def __prepare_tsne_traces(self):
        """
        Performs dimensionality reduction of train data + analyzed sample using
        t-SNE (t-distributed stochastic neighbor embedding).

        Returns
        -------
        list of dict
            list of dict for every possible label (result of prediction), each
            dict contains t-SNE coordinates of train data samples which were
            labeled with the corresponding label
        dict
            x and y coordinates of currently analyzed sample in diagram using
            t-SNE algorithm for reduction of dimensionality
        """

        labels = self.train_data['label'].tolist()
        data_files = self.train_data['data path'].tolist()
        data = self.train_data.drop(
            columns=['label', 'module path', 'data path'])

        # append sample module and get values
        sample_data = self.sample_data.drop(columns=['label'])
        data = data.append(sample_data, ignore_index=True)
        X = data.values

        X_std = StandardScaler().fit_transform(X)
        tsne = TSNE(n_components=2, perplexity=40)
        tsne_results = tsne.fit_transform(X_std)

        x = tsne_results[:, 0]
        y = tsne_results[:, 1]

        dimensions = len(data.columns)
        traces = [
            dict(x=list(), y=list(), text=list()) for _ in range(dimensions)
        ]

        # select sample point from results
        sample_trace = dict(x=x[len(x) - 1], y=y[len(y) - 1])

        # labels list doesn't contain sample data label, so it's OK to do this
        for i, label in enumerate(labels):
            traces[label]['x'].append(x[i])
            traces[label]['y'].append(y[i])
            traces[label]['text'].append(data_files[i])

        return traces, sample_trace

    def add_sample(self, sample: Sample):
        """
        If a sample wasn't provided when the Clusters instance was created,
        the sample can be added by this method. Data from provided sample are
        used to get activations from last layer and the prediction (label).
        Moreover, coordinates are determined for training data and currently
        analyzed sample using both t-SNE and PCA for dimensionality reduction.

        Parameters
        ----------
        sample : Sample
            instance of Sample representing currently analysed sample contained
            in JSON file
        """

        self.sample_data = self.__load_sample_data(sample)
        log.debug('Performing fit_transform for T-SNE...')
        self.tsne_traces, self.tsne_sample_trace = self.__prepare_tsne_traces()
        log.debug('Performing fit_transform for PCA...')
        self.pca_traces, self.pca_sample_trace = self.__prepare_pca_traces()
        log.debug('Successfully finished fit_transform...')

    def get_figure(self, algorithm: str, height=None) -> go.Figure:
        """
        Creates cluster diagram with coordinates calculated by given algorithm.
        It's optional to set the height of diagram in pixels.

        Parameters
        ----------
        algorithm : str
            'pca' or 'tsne', this parameter determines which coordinates
            should be used for dimensionality reduction
        height : int or None, optional
            height of diagram in pixels (default is None)

        Returns
        --------
        go.Figure
            go.Figure instance of cluster diagram
        """

        if algorithm == 'pca':
            traces = self.pca_traces
            sample_trace = self.pca_sample_trace
        else:
            traces = self.tsne_traces
            sample_trace = self.tsne_sample_trace

        fig = go.Figure()
        # add all cluster traces
        for i, trace in enumerate(traces):
            fig.add_trace(
                go.Scatter(
                    x=trace['x'],
                    y=trace['y'],
                    name='Label {}'.format(i),
                    text=trace['text'],
                    hoverinfo='x+y+text',
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=CLUSTER_COLORS[i],
                        opacity=0.6,
                    )
                )
            )

        # add sample point
        fig.add_trace(
            go.Scatter(
                x=[sample_trace['x']],
                y=[sample_trace['y']],
                name='Analyzed sample',
                mode='markers',
                hoverinfo='x+y',
                marker=dict(size=10, color='black')
            )
        )

        # add possible train samples for comparison
        for train_sample in self.train_samples:
            if train_sample:
                for i, trace in enumerate(traces):
                    if train_sample in trace['text']:
                        index = trace['text'].index(train_sample)
                        fig.add_trace(
                            go.Scatter(
                                x=[trace['x'][index]],
                                y=[trace['y'][index]],
                                hovertext=[trace['text'][index]],
                                mode='markers',
                                hoverinfo='x+y+text',
                                marker=dict(size=8, color=CLUSTER_COLORS[i],
                                            line=dict(width=2,
                                            color='DarkSlateGrey')),
                                showlegend=False
                            )
                        )
                        break

        fig.update_layout(
            height=height or 500,
            template='plotly_white',
            showlegend=True,
            hovermode='closest',
            margin={'l': 10, 'b': 10, 't': 20}
        )

        return fig

    def view(self, dash_id: str, columns: str, algorithm: str, height=None):
        """
        Creates dcc.Graph object which contains cluster diagram with
        coordinates calculated by given algorithm. It's optional to set
        the height of diagram in pixels.

        Parameters
        ----------
        dash_id : str
            id of the dcc.Graph component
        columns : str
            relative width of diagram, e.g. '6'
        algorithm : str
            'pca' or 'tsne', this parameter determines which coordinates
            should be used for dimensionality reduction
        height : int or None, optional
            height of diagram in pixels (default is None)

        Returns
        --------
        dcc.Graph
            dcc.Graph instance of cluster diagram
        """

        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(algorithm, height),
            style={
                'height': height or '40vh'
            },
            className=COLUMNS[columns]
        )
