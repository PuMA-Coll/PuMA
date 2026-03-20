#!/bin/bash

for i in $(ls *png); do

  bname=$(basename "$i")

  if [ ${bname%%.*}.jpg -nt $bname ]; then
    continue
#    echo "${bname%%.*}.jpg is up-to-date"
  else
    echo "Updating ${bname%%.*}.jpg ..."
    convert -thumbnail 400 $bname ${bname%%.*}.jpg
  fi

done

echo "Every thumbnail is up-to-date"
