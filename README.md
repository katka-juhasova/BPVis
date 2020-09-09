# CodeNNVis

Interactive visualization tool specialized for a neural network which
was designed to classify Lua source codes according to their structure. 
For more details about the NN, see https://github.com/krockamichael/bachelor_thesis.

The tool provides interface for analysis of the input data and its prediction 
as well as comparison of multiple data samples and their predictions. 
Multiple visualization methods are used to provide an explainability of the neural network.


![CodeNNVis GUI](https://github.com/katka-juhasova/CodeNNVis/blob/master/docs/gui.png)


## Installation 

- Install Git LFS (https://git-lfs.github.com). It's necessary since the repository uses Git LFS content.

```
git lfs install
```
- Download or clone this repository. The repository contains a submodule which needs to be properly downloaded as well. 
For proper cloning run:

```
git clone git@github.com:katka-juhasova/CodeNNVis.git
cd CodeNNVis
git submodule init
git submodule update
```

- Install requirements by running the command below. In case of some error with igraph library make sure that the correct version is downloaded from https://pypi.org/project/python-igraph/.
The error that may possibly occur is explained here: https://stackoverflow.com/questions/36200707/error-with-igraph-library-deprecated-library.
```
pip install -r requirements.txt
```
 
- Before running the application run the init script to preprocess and save the train data.
```
python3 init_script.py
```

## Using the visualization tool CodeNNVis

When everything is installed, simply run the CodeNNVis app. For Linux run `python3 CodeNNVis.py` from the root repository. 
The app shall be then running on http://127.0.0.1:8050/.

To start the analysis of the desired sample, enter its JSON file path from the data directory into the text box, e.g. for visualization of file `CodeNNVis/data/30log/AST1.json` write just `30log/AST1.json`.
Then press the submit button and wait for all the diagrams to load. The cluster diagram takes the longest to load due to the complex calculations necessary for the dimensionality reduction.

The components offer multiple interaction options.
The small colorful representation of the source code can be used to easily navigate through the original Lua code on the left side.
Both the tree diagram and the scatter plot offer various hover info and the legend can be used to hide/show desired traces.
The visualization of the prediction only displays activations from the last layer 
and activations from all of the layers can be shown/hidden after clicking on the option bellow the prediction.
The cluster diagram supports 2 methods for dimensionality reduction. The legend can be again used to determine which clusters should be visible.
Hover info in this diagram contains various information including the path of the samples. 
Whichever of these JSON paths can be entered as a sample path in the part for comparison of multiple samples. JSON paths can be entered repeatedly.
The comparison of multiple samples and their predictions can be done either by AST visualization or by colorful representation of the source code.
The samples that are being compared are also highlighted in the cluster diagram.
