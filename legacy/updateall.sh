#!/bin/bash

su aur <<'EOF'
repo_file="/srv/http/archlinux/vps.db.tar.gz"
packages_dir="/srv/http/archlinux"
root_dir="/aur"

new_packages=()

function build {
  makepkg -src --noconfirm --noprogressbar
  exitcode=$?
  validate_exit_code
}

function build_vcs {
  makepkg -sr --noconfirm --noprogressbar
  exitcode=$?
  validate_exit_code
}

function validate_exit_code {
  if [ "$exitcode" != "0" ]; then
    touch buildingfailed
    echo "==== BUILDING FAILED OR FILE ALREADY EXISTS ===="
    echo "Exit Code: $exitcode"
  else
    move_new_package
  fi
}

function move_new_package {
  package_name=`find . -name "*.pkg.tar.xz"`
  if [ "$package_name" != "" ]; then
    if [ "`cat lastpkgver`" != "$package_name" ]; then
      mv $package_name $packages_dir
      new_packages+=($package_name)
      echo "$package_name" > lastpkgver
    else
      echo "Same version as last."
    fi
  fi
}

function update_db {
  echo "Updating database..."
  for i in "${new_packages[@]}"; do
    echo "Adding $i to database."
    repo-add $repo_file $packages_dir/$i
  done
}

cd $root_dir
for dir in */; do
  echo "Updating $dir."
  cd $dir
  output="$(git pull)"
  if [ -e "needsbuilding" ]; then
    build
    rm needsbuilding
  fi
  if [ "$output" != 'Already up-to-date.' ]; then
    build
  elif [[ $dir == *"-git"* ]]; then
    build_vcs
  else
    echo "$dir is already up-to-date."
  fi
  cd ..
done
update_db
EOF

echo "Finished."
