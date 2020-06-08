import os
from constant import MODEL_NAME
from preprocessing.module_handler import ModuleHandler
from keras.models import load_model
from keras.models import Model
from network.utils import load_file
from network.clustering import ClusteringLayer
import numpy as np
from typing import List
import logging
import csv
import json

MAX_CONTEXTS = 430
here = os.path.dirname(os.path.realpath(__file__))
model_path = '{}/{}'.format(here, MODEL_NAME)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


# imitating Java's String#hashCode as the model is trained on hashed paths
def java_string_hashcode(s: str) -> int:
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF

    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


# module preprocessing, output can be used as input for NN
def build_input_from_json(json_path: str) -> np.ndarray:
    # get context paths
    module_handler = ModuleHandler(json_path)
    context_paths = module_handler.get_context_paths()

    # trim number of context paths if they exceed MAX_CONTEXTS
    while len(context_paths) > MAX_CONTEXTS * 2:
        # get every second element --> halve list length, this is FAST
        context_paths = context_paths[0::2]

    excess_contexts = len(context_paths) - MAX_CONTEXTS
    if excess_contexts > 0:
        new_contexts = list()
        for _, i in enumerate(context_paths):
            if _ < 2 * excess_contexts:
                if _ % 2 == 1:
                    new_contexts.append(i)
            else:
                context_paths = (
                    [x for x in context_paths if x not in new_contexts]
                )
                break

    # code context paths using java hash string
    file_context_paths = ''
    for i in context_paths:
        source_node = i[0][0] + '|' + i[0][1]
        hashed_source_node = java_string_hashcode(source_node)

        path = ''.join(i[1])
        hashed_path = java_string_hashcode(path)

        target_node = i[2][0] + '|' + i[2][1]
        hashed_target_node = java_string_hashcode(target_node)

        file_context_paths += (str(hashed_source_node) + ',' + str(hashed_path)
                               + ',' + str(hashed_target_node) + ' ')

    # do zero-padding
    if len(context_paths) < 430:
        for i in range(MAX_CONTEXTS - len(context_paths)):
            file_context_paths += '0,0,0 '

    # remove excess white-space at the end
    if file_context_paths[-1] == ' ':
        file_context_paths = file_context_paths[:-1]

    # generate dataset in the form of
    # (n_samples, n_context_paths, source_path_target)
    # shape(18000, 430)
    triplets = (
        [file_context_paths.replace('"', '').replace('\n', '').split(" ")]
    )
    # shape (18000, 430, 3)
    singles = []
    for t in triplets:
        singles += [[trp.split(',') for trp in t]]

    data = np.ma.array(singles).astype(np.int32)
    # values without zero-padding, to perform normalisation
    masked_data = np.ma.masked_equal(data, 0)

    # normalise data, get mean and std from training, here its hardcoded
    log.debug('Normalising data for JSON file "{}"'.format(json_path))
    masked_data_mean = 21.11153407758736
    masked_data_std = 1157761522.5453846

    # perform z-normalisation
    normalised_masked_data = (masked_data - masked_data_mean) / masked_data_std
    # refill masked values with 0
    final_data = normalised_masked_data.filled(0)

    return final_data


# pipeline for processing of 1 module and determining its label
def module_pipeline(json_path: str) -> int:
    # load the data
    data = build_input_from_json(json_path)

    # load model and generate label
    model = load_model(model_path,
                       custom_objects={'ClusteringLayer': ClusteringLayer})

    log.debug('Clustering model predicting...')
    x_model = model.predict(data)
    y_model = x_model.argmax(1)

    # module label
    return y_model[0]


# pipeline for predicting the whole dataset
def dataset_pipeline() -> np.ndarray:
    model = load_model(model_path,
                       custom_objects={'ClusteringLayer': ClusteringLayer})

    names, context_paths = load_file()
    train, validate, test = np.split(context_paths,
                                     [int(.7 * len(context_paths)),
                                      int(.9 * len(context_paths))])

    log.debug('Clustering model predicting...')
    x_model = model.predict(train)
    y_model = x_model.argmax(1)

    return y_model


# if the module is provided get activations for module, otherwise for
# whole dataset
def dataset_activations(layer=None) -> (List[str], dict):
    model = load_model(model_path,
                       custom_objects={'ClusteringLayer': ClusteringLayer})

    names, context_paths = load_file()
    train, valid, test = np.split(context_paths,
                                  [int(.7 * len(context_paths)),
                                   int(.9 * len(context_paths))])
    train_names, valid_names, test_names = np.split(names,
                                                    [int(.7 * len(names)),
                                                     int(.9 * len(names))])

    layers_count = len(model.layers)

    # if the layer number is chosen
    if layer and layer in range(layers_count):
        # choose output layer
        encoder = Model(inputs=model.layers[0].input,
                        outputs=model.layers[layer].output, name='encoder')

        log.debug('Predicting output layer {}'.format(layer + 1))
        x_encoder_model = encoder.predict(train)

        return train_names, {layer: x_encoder_model}

    # if the whole network should be tracked
    layer_outputs = dict()
    for i in range(layers_count):
        # choose output layer
        encoder = Model(inputs=model.layers[0].input,
                        outputs=model.layers[i].output, name='encoder')

        log.debug('Predicting output layer {}/{}'.format(i + 1, layers_count))
        x_encoder_model = encoder.predict(train)

        layer_outputs[i] = x_encoder_model

    return train_names, layer_outputs


# returns activations for just one module
# if layer is provided return activations of just one layer, otherwise for all
def module_activations(json_path: str, model=None, layer=None) -> dict:
    # load the data
    data = build_input_from_json(json_path)

    # load model and generate label
    model = (model or
             load_model(model_path, custom_objects={
                                    'ClusteringLayer': ClusteringLayer})
             )

    layers_count = len(model.layers)

    # if the layer number is chosen
    if layer and layer in range(layers_count):
        # choose output layer
        encoder = Model(inputs=model.layers[0].input,
                        outputs=model.layers[layer].output, name='encoder')

        log.debug('Predicting output layer {}'.format(layer + 1))
        x_encoder_model = encoder.predict(data)

        return {layer: x_encoder_model}

    # if the whole network should be tracked
    layer_outputs = dict()
    for i in range(layers_count):
        # choose output layer
        encoder = Model(inputs=model.layers[0].input,
                        outputs=model.layers[i].output, name='encoder')

        log.debug('Predicting output layer {}/{}'.format(i + 1, layers_count))
        x_encoder_model = encoder.predict(data)

        layer_outputs[i] = x_encoder_model

    return layer_outputs


# create csv files containing following info for each module from train data:
# module path, json path and activations from all layers
# 1st dimension separated by space and 2nd dimension by '|'
# activations from each layer are stored in separate files
def save_train_data_activations():
    path = os.path.dirname(os.path.realpath(__file__)) + '/../BP-data/data'
    data_files = list()

    # r=root, d=directories, f=files
    # list all json files
    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                data_files.append(os.path.join(r, file))

    module_names, outputs = dataset_activations()
    module_names = module_names.tolist()
    data_names = ['' for _ in range(len(module_names))]

    # assign corresponding file from ../data/
    for data_file in data_files:
        with open(data_file) as f:
            json_data = json.load(f)

        name = json_data['path']
        name = name.replace('BP-data/modules/', '')
        name = name[:-4]

        try:
            index = module_names.index(name)
            data_names[index] = data_file.replace('{}/../BP-data/data/'.format(
                os.path.dirname(os.path.realpath(__file__))), '')
        except ValueError:
            pass

    labels = outputs[len(outputs) - 1]
    labels = labels.argmax(1)

    rows_count = len(module_names)

    # write line for each module from train data
    # saves each layer to separate .csv file
    for layer in outputs:
        log.debug('Processing layer {}/{}'.format(layer + 1, len(outputs)))

        csv_header = ['data path', 'module path', 'label',
                      'layer{}'.format(layer)]

        with open('train_data_activations_layer{}.csv'.format(layer),
                  'w', newline='') as file:
            # write column names
            writer = csv.writer(file)
            writer.writerow(csv_header)

            for i in range(rows_count):
                csv_row = [data_names[i], module_names[i], labels[i]]

                activations = outputs[layer][i]
                final_activations = list()
                shape = activations.shape
                activations = activations.tolist()

                # handle 1D layer
                if len(shape) == 1:
                    activations = map(str, activations)
                    final_activations.append(' '.join(activations))

                # handle 2D layer
                elif len(shape) == 2:
                    tmp_activations = list()
                    for a in activations:
                        a = map(str, a)
                        tmp_activations.append(' '.join(a))

                    final_activations.append('|'.join(tmp_activations))

                csv_row.append(final_activations[0])
                writer.writerow(csv_row)
