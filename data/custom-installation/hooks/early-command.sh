#!/bin/sh
set -x

if [ -f /custom-installation/hooks/post-installer.sh ]; then
        mkdir -p  /root/usr/lib/ubiquity/target-config
	cp /custom-installation/hooks/post-installer.sh  /root/usr/lib/ubiquity/target-config/10post-installer
	chmod +x /root/usr/lib/ubiquity/target-config/10post-installer
fi

architecture=$(uname -m | sed s/i6/i3/)
if [ -f /custom-installation/patch/$architecture/parted_server ]; then
	cp /custom-installation/patch/$architecture/parted_server  /root/usr/bin/parted_server
        cp /custom-installation/patch/$architecture/libparted.so.0.0.1 /root/lib/$architecture-linux-gnu/libparted.so.0.0.1
        ln -s libparted.so.0.0.1 /root/lib/$architecture-linux-gnu/libparted.so.0
fi

