#!/bin/sh

rm -rf Couenne* coinhsl-linux-x86_64-2015.06.23

install_dir="/usr/local/share/coin-or"
sudo rm -rf $install_dir

bin_dir="/usr/local/sbin"
binaries="cbc clp ipopt bonmin couenne"
for binary in $binaries
do
  sudo rm -f $bin_dir/$binary
done