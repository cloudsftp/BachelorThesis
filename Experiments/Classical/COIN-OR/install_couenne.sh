#!/bin/sh

couenne_ver="0.5.8"
couenne_name="Couenne-$couenne_ver"

cd $couenne_name/build

num_cores="$(cat /proc/cpuinfo | grep processor | wc -l)"
sudo make install -j $num_cores

install_dir="/usr/local/share/coin-or"
bin_dir="/usr/local/sbin"
binaries="cbc clp ipopt bonmin couenne"

for binary in $binaries
do
  sudo rm $bin_dir/$binary
  sudo ln -s $install_dir/bin/$binary $bin_dir/$binary
done