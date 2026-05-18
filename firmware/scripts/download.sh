#!/bin/bash

declare -a Builds=(
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/13/Upgrade_Build%2013.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/12/Upgrade_Build_15_v2.2.5.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/10/build_17_v3.4.1.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/11/upgrade_build_16_v3.2.5.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/9/build_20_v20.1.3.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/8/build_20_v20.1.6.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/7/build_21_v21.4.1.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/69/build_30_v30.7.0.zip"
	"https://s3.amazonaws.com/rdc_us/system/downloads/files/145/build_31_v31.6.16.zip"
	"https://s3.amazonaws.com/red-4/downloads/firmware/red_one/build_32_v32.0.3.zip"
	)



for i in ${Builds[@]}; do
   wget "$i"
done
