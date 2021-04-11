# COIN-OR Couenne

## Build from Source [Optional]

To build Couenne from source, run `./build_couenne.sh`

The build can be deleted by running `./clean_build.sh`

To install the files built from source run `./install_couenne.sh`

## Without Installation

Only the `coinhsl`-libraries have to be extracted.
For this sinmply execute the script `extract_coinhsl.sh`.

The libraries are added with the setup script `setup.sh` in the `Experiments` directory.
Also the path to the `couenne` binary is added to the `$PATH` via that script.
No installation is required.

If it does not work, please follow the instructions above and build Couenne from Source.
