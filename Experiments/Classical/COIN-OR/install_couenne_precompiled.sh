#!/bin/sh

cd Couenne_binaries

install_dir="/usr/local/share/coin-or"
bin_dir="/usr/local/sbin"
binaries="cbc clp ipopt bonmin couenne"

sudo mkdir $install_dir
sudo cp -r * $install_dir

for binary in $binaries
do
  sudo rm $bin_dir/$binary
  sudo ln -s $install_dir/bin/$binary $bin_dir/$binary
done

sudo chmod +x $install_dir/bin/*