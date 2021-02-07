#!/bin/sh

env_file="conda_environment.yml"
echo Creating conda environment from $env_file
echo
if [ -z "$(conda env list | grep opt)" ]
then
  conda env create -f $env_file
else
  conda env update -f $env_file
fi
