# BPVis

Interactive visualization tool for deep neural network.

## How to run with loading from local files

- Download (clone or whatever) this repository.
- Download repository https://github.com/katka-juhasova/BP-data.
- Create directories `data` and `modules` in cloned BPVis repository.
Repository tree should look now like this:


    BPVis
        ├── app_demo.py
        ├── assets
        ├── components
        ├── constant.py 
        ├── data
        ├── LICENSE
        ├── modules 
        ├── preprocessing
        ├── README.md 
        ├── requirements.txt
        └── setup.py


- Content of `data-part1` and `data-part2` directories (from BP-data repository) move to `data` directory.
- Content of `modules-part1` and `modules-part2` directories (from BP-data repository) move to `modules` directory.
- Run `python3 script.py <BPVis_repository_path>` e.g. `python3 script.py '/home/BPVis'
` (from BP-data repository). Directory `data` contains only .json representations of modules, 
full source code is contained in `modules`. This script adds path to the downloaded modules, otherwise, the modules content
would be read from git url and it would take like forever to run the app.
- Install requirements. In case of some error with igraph library make sure that you downloaded correct version from https://pypi.org/project/python-igraph/.
The error that might have occurred is explained here: https://stackoverflow.com/questions/36200707/error-with-igraph-library-deprecated-library.
- Run `python3 app_demo.py` from this repository. App is now running on http://127.0.0.1:8050/.

For visualization of other modules change lines `file_left = files[0]` and `file_right = files[1]` in app_demo.py. 
You can change just index or assign path to the .json file, e.g. `/home/BPVis/data/30log/AST1.json` or `data/30log/AST1.json` for Linux. In that case it might just take a little bit longer to run the app.

NOTE: interesting tree visualizations:
    
    <BPVis_repository_path>/data/30log/AST1.json
    <BPVis_repository_path>/data/30log/AST1.json


