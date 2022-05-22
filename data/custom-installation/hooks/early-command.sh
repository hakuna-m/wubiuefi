#!/bin/sh
set -x

##
## copy from scripts/casper-bottom/05mountpoints_lupin
##
if grep -q '^[^ ]* /isodevice ' /proc/mounts; then
	mkdir -p /root/isodevice
	mount -n -o move /isodevice /root/isodevice
fi

if [ -n $1 ] && [ -d "/root/isodevice$1" ]; then
##
## replacement for the necessary parts of scripts/casper-premount/30custom_installation
##
	mkdir -p /custom-installation
	cp -af "/root/isodevice$1"/* /custom-installation/
	if [ -e /custom-installation/preseed.cfg ]; then
		cp /custom-installation/preseed.cfg /
		dev=$(cat /proc/mounts | grep '^[^ ]* /root/isodevice ' | cut -f 1 -d ' ')
		disk="$(echo "$dev" | sed 's/[0-9]*$//')"
		partn=${dev#${disk}}
		sed -i "s:LIDISK:$disk:g" /preseed.cfg
		sed -i "s:LIPARTITION:$partn:g" /preseed.cfg
		dev=${dev#/dev/}
		sed -i "s:MADEVICE:$dev:g" /preseed.cfg
	fi
##
## copy from scripts/casper-bottom/10custom_installation
##
	cp -af /custom-installation/ /root/custom-installation || true
	if [ -x /custom-installation/hooks/casper-bottom.sh ]; then
		/custom-installation/hooks/casper-bottom.sh
	fi
##
## copy from scripts/casper-bottom/24preseed
##
	if [ -e /preseed.cfg ]; then
		casper-set-selections /preseed.cfg
	fi
fi

if [ -f /custom-installation/hooks/post-installer.sh ]; then
        mkdir -p  /root/usr/lib/ubiquity/target-config
	cp /custom-installation/hooks/post-installer.sh  /root/usr/lib/ubiquity/target-config/10post-installer
	chmod +x /root/usr/lib/ubiquity/target-config/10post-installer
fi

if [ -f /custom-installation/patch/autopartition-loop ]; then
	cp /custom-installation/patch/autopartition-loop  /root/bin/autopartition-loop
fi

if [ -f /custom-installation/patch/user-params ]; then
	cp /custom-installation/patch/user-params  /root/bin/user-params
fi

# create dummy loop device for autopartition-loop
mkdir -p /tmp/loopdummy
touch /tmp/loopdummy/loopdummy
modprobe loop
ln -s $(losetup -f) /dev/loopdummy
losetup /dev/loopdummy /tmp/loopdummy/loopdummy
