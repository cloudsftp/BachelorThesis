#!/bin/sh

apt_packages_file="packages.list"
echo Installing linux packages from file $apt_packages_file
echo
grep -vE '^#' $apt_packages_file | xargs sudo apt install -y

echo
env_file="conda_environment.yml"
echo Creating conda environment from $env_file
echo
if [ -z "$(conda env list | grep opt)" ]
then
  conda env create -f $env_file
else
  conda env update -f $env_file
fi
