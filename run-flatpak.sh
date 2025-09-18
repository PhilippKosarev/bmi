#! /usr/bin/env bash
set -u

# Imports
source cfgrun.sh
source librun.sh

# Running
bold-echo 'Building...' &&
subcommand "flatpak-builder --force-clean $build_dir $manifest" &&

bold-echo 'Application started:' &&
subcommand "flatpak-builder --run $build_dir $manifest $bin"
bold-echo 'Application stopped.'