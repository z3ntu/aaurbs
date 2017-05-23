#!/usr/bin/env bash

set -e

basepath=$(grep "base_path" config.py | cut -d'=' -f2 | sed 's/"//g' | xargs)

if [ ! -d "$basepath" ]; then
    echo "Found $basepath in base_path variable in config.py which doesn't seem valid! Potentially the issue is that you are using single quotes instead of double quotes (which isn't handled by this script)."
    echo "Exiting."
    exit 1
fi

extensions=(deb zip tar.gz tar.xz tar.bz2 bin)

for i in ${extensions[@]}; do
    echo "Removing files with the extension: $i"
    rm -v "$basepath"/packages/*/*."$i" || true
done

echo "Done."
