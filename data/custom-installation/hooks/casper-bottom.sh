#!/bin/sh

#fix wrong linux device names of MMCs and NVMe devices in preseed.cfg
if [ -e /preseed.cfg ]; then
	sed -i "s:\(d-i partman-auto/disk string /dev/mmcblk[0-9]\)p:\1:g" /preseed.cfg
	sed -i "s:\(d-i partman-auto/disk string /dev/nvme[0-9][0-9]*n[0-9][0-9]*\)p:\1:g" /preseed.cfg
fi






