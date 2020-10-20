#!/bin/sh

sudo echo Password saved for script

# Download and extract Couenne

couenne_ver="0.5.8"
couenne_name="Couenne-$couenne_ver"
couenne_arch="$couenne_name.tgz"

if [ -z "$(ls | grep ^$couenne_arch\$)" ]
then
  wget https://www.coin-or.org/download/source/Couenne/$couenne_arch
fi

if [ -z "$(ls | grep ^$couenne_name\$)" ]
then
  tar xfz $couenne_arch
  echo Extracting $couenne_arch
  echo
fi

cd $couenne_name

# Download free third party software

cd ThirdParty

thirdparty_softwarepackages="ASL Blas Lapack Metis"
for name in $thirdparty_softwarepackages
do
  cd $name
  ./get.$name
  cd ..
done

cd ..

# Build Couenne

build_dir="build"
install_dir="/usr/local/share/coin-or"

mkdir $build_dir
cd $build_dir
../configure -C --prefix=$install_dir #$hsl_configure_flags
make

# Install Couenne

sudo make install

bin_dir="/usr/local/sbin"
binaries="cbc clp ipopt bonmin couenne"

for binary in $binaries
do
  sudo ln -s $install_dir/bin/$binary $bin_dir/$binary
done