#/bin/sh

env="$CONDA_DEFAULT_ENV"
env_config_file="conda_environment.yml"

if [ "$env" = "opt" ]
then
  echo Exporting conda environment $env to $env_config_file...
  conda env export | grep -v ^prefix: > $env_config_file
else
  echo Make sure, $env is activated when exporting!
fi