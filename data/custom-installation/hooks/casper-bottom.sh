#!/bin/sh

#fix wrong linux device names of MMCs in preseed.cfg
if [ -e /preseed.cfg ]; then
	sed -i "s:\(d-i partman-auto/disk string /dev/mmcblk[0-9]\)p:\1:g" /preseed.cfg
fi






