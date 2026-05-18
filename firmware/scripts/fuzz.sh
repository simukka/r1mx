#!/bin/bash

declare -a Builds=(
  "build_4_red_one_v1.0.4"
  "build_5_red_one_v1.1.2"
  "build_6_red_one_v1.1.3"
  "build_8_red_one_v1.3.5"
  "build_8_red_one_v1.3.6"
  "build_10_red_one_v1.7.0"
  "build_10_red_one_v1.8.6"
  "build_12_red_one_v1.8.8"
  "build_15_red_one_v2.2.5"
  )




for i in {123..999}; do
  printf "\n$i\n"

  for b in ${Builds[@]}; do
    url="https://s3.amazonaws.com/rdc_us/system/downloads/files/$i/$b.zip"
    status_code=$(curl --write-out %{http_code} --silent --output /dev/null ${url})

    if [[ "$status_code" == 200 ]]; then
      printf "\n$url\n"
    elif [[ "$status_code" == 403 ]]; then
      printf "x"
    else
      printf "?"
    fi
  done
done
