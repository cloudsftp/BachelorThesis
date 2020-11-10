#!/bin/sh

hsl_ver="2015.06.23"
hsl_name="coinhsl-linux-x86_64-$hsl_ver"
hsl_arch="$hsl_name.tar.gz"

if [ -z "$(ls | grep ^$hsl_name\$)" ]
then
  tar xfz $hsl_arch
  echo Extracting $hsl_arch
  echo
fi

install_dir="/usr/local/share/hsl"

sudo rm -rf $install_dir
sudo mkdir $install_dir
sudo cp $hsl_name/* $install_dir/ -r

sudo cp Libgfortran/* $install_dir/lib/

sudo ln -s $install_dir/lib/libcoinhsl.so.0 $install_dir/lib/libhsl.so