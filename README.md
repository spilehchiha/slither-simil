# SlithIR Extraction and Processing

The SlithIR extraction script should be located in the top-level directory as to the project to be analyzed in order for it to avoid compilation errors.

Run the script in the `smart-contract-clients` directory.

Also, in order to successfully run [the Slither-simil fork by `@spilehchiha`](https://github.com/spilehchiha/slither), you need to first clone the `smart-contract-clients` repository from ToB.
Then, `cd` into the `contracts_audited` directory, and then train or test.

Training and testing procedures are almost the same as before, with the exception of using the keyword `trainfunction` instead of the usual `train`.


While training, a `cache.npz` file of the input serialized file is also created in the same directory which can be used while testing.

To test:
```
slither-simil test [created_model_name.bin] --filename [file_name] --fname [function_name] --input cache.npz --ntop 35
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
