import os
from sample import Sample
import pandas as pd
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from constant import CLUSTER_COLORS
from constant import COLUMNS
import dash_core_components as dcc


CSV_PATH = (os.path.dirname(os.path.realpath(__file__))
            + '/../network/train_data_activations_layer4.csv')


class Clusters:
    def __init__(self, sample: Sample):
        self.sample_data = self.__load_sample_data(sample)
        self.train_data = self.__load_train_data()
        self.tsne_traces, self.tsne_sample_trace = self.__prepare_tsne_traces()
        self.pca_traces, self.pca_sample_trace = self.__prepare_pca_traces()

    @staticmethod
    def __load_sample_data(sample: Sample) -> pd.DataFrame:
        df = pd.DataFrame()
        df['label'] = sample.label
        last_layer = list(sample.activations.keys())[-1]
        activations = sample.activations[last_layer][0].tolist()
        for i, activation in enumerate(activations):
            df['d{}'.format(i)] = [activation]

        return df

    @staticmethod
    def __load_train_data() -> pd.DataFrame:
        df = pd.read_csv(CSV_PATH)
        layer = [l for l in df.columns if 'layer' in l][0]
        dimensions = str(df[layer][0]).split(' ')
        dimensions = ['d{}'.format(d) for d in range(len(dimensions))]
        df[dimensions] = df[layer].str.split(expand=True)
        df = df.drop(columns=[layer])

        return df

    def __prepare_pca_traces(self):
        labels = self.train_data['label'].tolist()
        data_files = self.train_data['data path'].tolist()
        data = self.train_data.drop(
            columns=['label', 'module path', 'data path'])

        # append sample module and get values
        sample_data = self.sample_data.drop(columns=['label'])
        data = data.append(sample_data, ignore_index=True)
        X = data.values

        X_std = StandardScaler().fit_transform(X)
        pca = PCA(n_components=6)
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

    def get_figure(self, algorithm: str) -> go.Figure:
        if algorithm == 'PCA':
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

        fig.update_layout(
            template='plotly_white',
            showlegend=True,
            hovermode='closest'
        )

        return fig

    def view(self, dash_id: str, columns: str, algorithm: str, height=None):
        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(algorithm),
            style={
                'height': height or '40vh'
            },
            className=COLUMNS[columns]
        )
