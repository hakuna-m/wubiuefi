#!/bin/sh
set -x

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
