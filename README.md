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

Now that everything is installed, simply run the CodeNNVis app. For Linux run `python3 CodeNNVis.py` from this repository. 
App shall be then running on http://127.0.0.1:8050/.

To start the analysis of the desired sample, enter its relative JSON file path (from the data directory) into the text box, e.g. for visualization of file `CodeNNVis/data/30log/AST1.json` write just `30log/AST1.json`.

Then press the submit button and wait for all the diagrams to load. The cluster diagram takes the longest due to the complex calculations necessary for the dimensionality reduction.

The components support multiple option for interaction.

- scrollovatelny ofarbeny realny kod
- zahustena farebna reprezentacia kodu, ktora ide pouzit na navigaciu vo velkom, staci kliknut 
na cast a originalny cod a scrollne na tu cast
- tree a scatter plot offer various hover info a po kliknuti na traces v lgend mozu byt skryte alebo opatovne zobrazene
- prediction poskytuje tiez hover info, ta zaobrazuje last layer activations, for activations on all of the layers
click the option to view/hide nieco co je za tym
- cluster diagram supports 2 methods for reduction of dimensionality, po kliknuti na traces v lgend mozu byt skryte alebo opatovne zobrazene
- whichever JSON path from cluster diagram can be enetered do policok v porovnavacej casti
- comparison of multiple samples and their predictions can be done either by AST vizualization or by colorful representation of the source code
- JSON paths can be entered repeatadly

