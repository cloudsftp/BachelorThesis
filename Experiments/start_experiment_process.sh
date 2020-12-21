#!/bin/sh

node="0"

if [ "$1" = "--node" ]; then
  cpu="$2"
  shift
  shift
fi

output_file=experiment_output.log
numactl --physcpubind=$node --membind=$node \
  python -m Classical.perform_experiments $@ > $output_file &
