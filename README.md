# Slither-Simil: A Statistical Analysis Framework for Smart Contracts

The corresponding wiki page is available [page.](https://github.com/crytic/slither/wiki/Code-Similarity-detector)

## Installation and Setup

Install `solc-select`:
```
pip3 install solc-select
```

Fork and build from this branch of Slither:
```
git clone -b slither-simil-vul-function  https://github.com/spilehchiha/slither.git
```

Fork crytic_compile:
```
https://github.com/spilehchiha/crytic-compile/tree/dev-zip
```

[Guide on using git-lfs](https://docs.github.com/en/github/managing-large-files/installing-git-large-file-storage)

Take the `output.csv` (in the private issues repo) file and the `datasets/15kdump_model.bin` file already in the repository and use it as follows:

`slither-simil test [datasets/15kdump_model.bin] --filename [file_name] --fname [function_name]  --input [input_file] --ntop [n]`

[file_name]: can be a singleton file name or a directory path, containing multiple smart contracts either in .sol or .zip formats or a combination of both

[function_name]: with or without the preceding contract name (as in contract_name[.]function_name) or a simple dot mark, meaning all the functions in the contracts provided by the previous argument flag;

[input_file]: A cache.npz file or an csv file containing contracts adn functions (for internal use)

[n]: any integer greater than zero.


