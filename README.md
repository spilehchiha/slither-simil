# SlithIR Extraction and Processing

There is a wiki page available for `slither-simil` on this [page.](https://github.com/crytic/slither/wiki/Code-Similarity-detector)

## Installation and Setup

Install `solc-select`:
```
pip3 install solc-select
```

Fork this Slither repository's branch and build from this version of `slither-simil`:
```
git clone -b slither-simil-vul-function  https://github.com/spilehchiha/slither.git
```

You also need this specific fork of crytic_compile:
```
https://github.com/spilehchiha/crytic-compile/tree/dev-zip
```

Guide on using git-lfs: Go to this [link.](https://docs.github.com/en/github/managing-large-files/installing-git-large-file-storage)

Take the `output.csv` (in the private issues repo) file and the `datasets/15kdump_model.bin` file already in the repository and use it as follows:
```
slither-simil test [datasets/15kdump_model.bin] --filename [file_name; can be a singleton file name or a directory path containing multiple smart contracts either in .sol or .zip formats or a combincation of both] --fname [function_name with or without the preceding contract name (as in contractname[.]functionname) or a simple dot mark, meaning all the functions in the contracts provided by the previous argument flag;] --input [cache.npz or output.csv] --ntop [n; an ineteger; e.g. 3]
```
