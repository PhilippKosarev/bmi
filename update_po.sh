#!/bin/bash

echo "Updating pot file."
xgettext --files-from=po/POTFILES.in --output=po/bmi.pot --join-existing --omit-header
po_files=($(find ./po/ -name *.po))
echo "Updating: ${po_files[@]}"
for file in ${po_files[@]}; do
  msgmerge $file po/bmi.pot -U
done