#!/bin/bash

su aur <<EOF
git clone "https://aur.archlinux.org/$1.git"
touch $1/needsbuilding
EOF

echo "Finished."
