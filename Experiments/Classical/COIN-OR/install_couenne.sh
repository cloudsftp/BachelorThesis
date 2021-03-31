#!/bin/sh

couenne_ver="0.5.8"
couenne_name="Couenne-$couenne_ver"

cd $couenne_name/build

num_cores="$(cat /proc/cpuinfo | grep processor | wc -l)"
sudo make install -j $num_cores
