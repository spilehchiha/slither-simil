The SlithIR representation extraction script should be located in the top-level directory as to the project to be analyzed in order to avoid compilation errors.

Just run the script in the `smart-contract-clients` directory and provide the arguments `model.bin`, and a file containing serialized SlithIRs od functions. One such file is provided in this repository.

Also, in order to successfully run [the Slither-simil fork by `@spilehchiha`](https://github.com/spilehchiha/slither), you need to first clone the `smart-contract-clients` repository from ToB.
Then, `cd` into the `contracts_audited` directory, and then train or test.

Training and testing procedures are almost the same as before, with the exception of using the keyword `trainfunction` instead of the usual `train`.

To train:
```
slither-simil trainfunction [model_name.bin] --input [slithIR-serialized_file]
```

While training, a `cache.npz` file of the issues dataset is also created in the same directory which can be used while testing.

To test:
```
slither-simil test [model_name.bin] --filename [file_name] --fname [function_name] --input cache.npz --ntop 35
```


