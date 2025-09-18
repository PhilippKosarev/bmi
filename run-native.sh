#! /usr/bin/env bash
set -u

# Imports
source cfgrun.sh
source librun.sh

# Running
bold-echo 'Configuring...' &&
subcommand "rm -rf $build_dir" &&
subcommand "mkdir $build_dir" &&
subcommand "meson setup $build_dir --prefix=$prefix" &&

bold-echo 'Compiling...' &&
subcommand "meson compile -C $build_dir" &&

bold-echo 'Installing...' &&
subcommand "meson install -C $build_dir" &&

bold-echo 'Application started:' &&
$bin
bold-echo 'Application stopped.'

bold-echo 'Uninstalling...' &&
subcommand "ninja uninstall -C $build_dir"