#!/bin/sh

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
../configure -C --prefix=$install_dir

num_cores="$(cat /proc/cpuinfo | grep processor | wc -l)"
make -j $num_cores