#!/bin/sh

install_dir="/usr/local/share"
sudo rm -rf $install_dir/coin-or $install_dir/hsl

bin_dir="/usr/local/sbin"
binaries="cbc clp ipopt bonmin couenne"
for binary in $binaries
do
  sudo rm -f $bin_dir/$binary
done