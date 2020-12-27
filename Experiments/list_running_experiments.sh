#!/bin/sh

echo Currently running experiments:
echo

ps -aux | grep 'python -m Classical.perform_experiments' | grep -v grep
