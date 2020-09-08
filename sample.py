import logging
import json
import urllib
from network.pipeline import module_activations


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Sample:
    """
    Class containing everything needed for visualization of the sample.

    Attributes
    ----------
    data : dict
        content of JSON file which contains preprocessed data
    activations : dict
        activations from all 5 layers of NN for given JSON file
    label : int
        result (prediction) of NN for given JSON file
    """

    def __init__(self, path=None, url=None, model=None):
        """
        Reads JSON file either from the provided path or url, therefore one of
        these values has to be not None. If path to the NN model is provided,
        then the model is loaded as well.

        Parameters
        ----------
        path : str or None, optional
            path to the JSON file which contains preprocessed LUA source code
            (default is None)
        url : str or None, optional
            url of the JSON file which contains preprocessed LUA source code
            (default is None)
        model : str or None, optional
            path to the trained NN model (default is None)
        """

        if all(arg is None for arg in {path, url}):
            raise ValueError('Expected either path or url argument')

        if path:
            with open(path) as f:
                self.data = json.load(f)

        else:
            log.debug('Loading data file from {}'.format(url))
            with urllib.request.urlopen(url) as url_data:
                self.data = json.loads(url_data.read().decode())

        self.activations = module_activations(json_path=path, model=model)
        last_layer = list(self.activations.keys())[-1]
        self.label = self.activations[last_layer].argmax(1)[0]
