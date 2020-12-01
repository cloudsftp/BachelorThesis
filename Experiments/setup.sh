#!/bin/sh

# Activate conda environment
conda activate opt

# Couenne installation
coin_or_home="$(pwd)/Classical/COIN-OR"

export PATH=$coin_or_home/Couenne/bin:$PATH

# Add hsl path to library path
coinhsl_dir_name="coinhsl-linux-x86_64-2015.06.23"

coinhsl_dir="$coin_or_home/$coinhsl_dir_name"
coinhsl_archive="$coinhsl_dir.tar.gz"

if [ ! -d $coinhsl_dir ]; then
  tar xfz $coinhsl_archive -C $coin_or_home
fi

libhsl_link="$coinhsl_dir/lib/libhsl.so"
if [ ! -f $libhsl_link ]; then
  ln -s libcoinhsl.so.0 $libhsl_link
fi

export LD_LIBRARY_PATH=\
$coin_or_home/Couenne/lib:\
$coin_or_home/$coinhsl_dir_name/lib:\
$coin_or_home/Libgfortran:\
$LD_LIBRARY_PATH
