#! /bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

# Configuring
echo "${bold}Configuring...${normal}" &&
rm "./build" -rf &&
mkdir "./build" &&
meson setup "build" > /dev/null &&
cd "./build" &&
# Compiling
echo "${bold}Compiling...${normal}" &&
meson compile > /dev/null &&
# Installing
echo "${bold}Installing...${normal}" &&
sudo meson install > /dev/null &&
# Launching app
echo "${bold}Application started:${normal}" &&
bmi &&
echo "${bold}Application stopped.${normal}" &&
# Uninstalling
echo "${bold}Uninstalling...${normal}"
uninstall_log=$(sudo ninja uninstall)
if [[ $(echo "$uninstall_log" | grep 'Failed:') != 'Failed: 0' ]]; then
  echo "$uninstall_log"
fi
cd '..'