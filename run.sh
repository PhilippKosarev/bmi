#! /bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

# Configuring
echo "Configuring..." &&
rm "./build" -rf &&
mkdir "./build" &&
meson setup "build" > /dev/null &&
cd "./build" &&
# Compiling
echo "Compiling..." &&
meson compile > /dev/null &&
# Installing
echo "Installing..." &&
sudo meson install > /dev/null &&
# Launching app
echo "${bold}Application started:${normal}" &&
bmi &&
echo "${bold}Application stopped.${normal}" &&
# Uninstalling
echo "Uninstalling..."
uninstall_log=$(sudo ninja uninstall)
if [[ $(echo "$uninstall_log" | grep 'Failed:') != 'Failed: 0' ]]; then
  echo "$uninstall_log"
fi
cd '..'