#!/bin/sh
set -x

if [ -f /custom-installation/hooks/post-installer.sh ]; then
        mkdir -p  /root/usr/lib/ubiquity/target-config
	cp /custom-installation/hooks/post-installer.sh  /root/usr/lib/ubiquity/target-config/10post-installer
	chmod +x /root/usr/lib/ubiquity/target-config/10post-installer
fi



