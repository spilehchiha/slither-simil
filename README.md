# SlithIR Extraction and Processing

There is a wiki page available for `slither-simil` on this [page.](https://github.com/crytic/slither/wiki/Code-Similarity-detector)


## Installation adn Setup

Install `solc-select` via git (Use on Linux for now.):
```
https://github.com/crytic/solc-select
```

Fork this specific branch and build from this version of `Slither-simil`:
```
git clone -b slither-simil-vul-function  https://github.com/spilehchiha/slither.git
```

You also need this specific fork of crytic_compile:
```
https://github.com/spilehchiha/crytic-compile/tree/dev-zip
```

On git-lfs: Go to this [link.](https://docs.github.com/en/github/managing-large-files/installing-git-large-file-storage)

Some SlithIRs have already been extracted and are located as `datasets/output.csv`.

Take the `output.csv` file and the `datasets/15kdump_model.bin` file already in the repository and use it as follows:
```
slither-simil test [datasets/15kdump_model.bin] --filename [file_name; can be a singleton file name or a directory path containing multiple smart ontracts either in .sol or .zip formats or a c ombincation of both] --fname [function_name with or without the preciding contract name (as in contractname[.]functionname) or a simple dot mark, meaning all the functions in the contracts provided by the previous argument flag;] --input [cache.npz or output.csv] --ntop [n; an ineteger; e.g. 3]
```
