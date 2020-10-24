#!/bin/sh

# Activate conda environment
conda activate opt

# Add hsl path to library path
export LD_LIBRARY_PATH=/usr/local/share/hsl/lib:$LD_LIBRARY_PATH