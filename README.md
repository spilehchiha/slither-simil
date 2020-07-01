# SlithIR Extraction and Processing

Do not yet test this tool on `.zip` smart contracts, but on `.sol` ones.

Use fastText version 0.2.0 and not an upgraded one:
```
$ pip3 install https://github.com/facebookresearch/fastText/archive/0.2.0.zip --user
```

Fork this specific branch and build from this version of `Slither-simil`:
```
git clone -b slither-simil-vul-function  https://github.com/spilehchiha/slither.git
```

Some SlithIRs have already been extracted and are located as `slithIR_serialized_file.`

1. Use the `train` command to get the cache file consistig of pre-computed vectors for `slithIR_serialized_file:
```
slither-simil train [new_model_name.bin] --input [slithIR-serialized_file]
```

2. discard the generated `model.bin` file as we don't need it. We are only interested in the generated `cache.npz` file.

3. Take the `cache.npz` file and the `15kdump_model.bin` file already in the repository and use it as follows:
```
slither-simil test [15kdump_model.bin] --filename [file_name; can be a singleton file name or a directory path containing multiple smart ontracts] --fname [function_name; pure identifier here; no contract name needed] --input cache.npz --ntop [n; an ineteger; e.g. 3]
```
