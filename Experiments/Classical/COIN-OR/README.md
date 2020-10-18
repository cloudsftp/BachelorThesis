# Install Classical Solver

## [Couenne](https://projects.coin-or.org/Couenne)

1. Download [Source](https://www.coin-or.org/download/source/Couenne).
1. Install Third Party Software (ASL, Blas, Lapack)
1. `mkdir build && cd build`
1. `../configure -C --prefix=/usr/local/share/coin-or`
1. `make`
1. `sudo make install`
1. `./add_coinor_to_path.sh`

After that, `libhsl.so` is required.
1. Download [here](http://www.hsl.rl.ac.uk/download/coinhsl-linux-x86_64/2015.06.23/)
1. Make library loadable at runtime (Copy library file `libhsl.so` to `/usr/local/share/coin-or`)
