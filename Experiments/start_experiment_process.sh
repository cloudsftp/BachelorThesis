#!/bin/sh

node="0"

if [ "$1" = "--node" ]; then
  cpu="$2"
  shift
  shift
fi

source setup_environment.sh

output_file=experiment_node${node}_output.log

numactl --physcpubind=$node --membind=$node \
  python -m Classical.perform_experiments $@ > $output_file &
