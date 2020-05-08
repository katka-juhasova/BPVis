import logging
import json
import urllib
from network.pipeline import module_activations


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


# class containing everything needed for visualization of sample
class Sample:
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

        self.activations = module_activations(json_path=path)
        last_layer = list(self.activations.keys())[-1]
        self.label = self.activations[last_layer].argmax(1)[0]
