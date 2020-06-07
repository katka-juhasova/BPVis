# CodeNNVis

Interactive visualization tool for deep neural network.

## How to run with loading from local files

- Download (clone or whatever) this repository.
- Download repository https://github.com/katka-juhasova/BP-data.
- Create directories `data` and `modules` in cloned CodeNNVis repository.
Repository tree should look now like this:


    BPVis
        ├── assets
        ├── CodeNNVis.py
        ├── components
        ├── constant.py 
        ├── data
        ├── LICENSE
        ├── modules 
        ├── network
        ├── preprocessing
        ├── README.md 
        ├── requirements.txt
        └── sample.py


- Content of `data-part1` and `data-part2` directories (from BP-data repository) move to `data` directory.
- Content of `modules-part1` and `modules-part2` directories (from BP-data repository) move to `modules` directory.
- Install requirements. In case of some error with igraph library make sure that you downloaded correct version from https://pypi.org/project/python-igraph/.
The error that might have occurred is explained here: https://stackoverflow.com/questions/36200707/error-with-igraph-library-deprecated-library.
- For Linux run `python3 CodeNNVis.py` from this repository. App is now running on http://127.0.0.1:8050/.

In application GUI enter relative JSON file paths from data directory, e.g. for visualization of `file data/30log/AST1.json` write just `30log/AST1.json`.


