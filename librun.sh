#! /usr/bin/env bash
set -u

BOLD=$(tput bold)
RESET=$(tput sgr0)
function bold-echo {
  echo "${BOLD}$1${RESET}"
}
function subcommand {
  output="$($1)"
  status=$?
  if [[ $status != 0 ]]; then
    echo
    bold-echo "Command '$1' failed."
    echo "$output"
    echo
  fi
  return $status
}