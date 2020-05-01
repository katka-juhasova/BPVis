import logging
import numpy as np
from typing import List


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


# load all acquired preprocessed modules and their names from csv file
def load_file() -> (List[str], np.ndarray):
    filename = 'final_dataset.csv'
    with open(filename, 'r') as file:
        lines = file.readlines()

    file.close()

    log.debug('Processing input file "{}"'.format(filename))
    # shape (18000, 430)
    triplets = [l.replace('"', '').replace('\n', '').split(" ") for l in lines]
    # shape (18000, 430, 3)
    singles = []
    for t in triplets:
        singles += [[trp.split(',') for trp in t]]

    names = []  # get file names
    for single in singles:
        names += single[0]
        single.remove(single[0])

    data = np.ma.array(singles).astype(np.int32)
    masked_data = np.ma.masked_equal(data, 0)  # values without zero-padding

    # normalise data
    log.debug('Normalising data...')
    # perform z-normalisation
    normalised_masked_data = ((masked_data - masked_data.mean())
                              / masked_data.std())

    # refill masked values with 0
    final_data = normalised_masked_data.filled(0)

    return names, final_data
